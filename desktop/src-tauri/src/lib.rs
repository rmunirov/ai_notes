// AI Notes: optional embedded Python API via `uv run python -m ai_notes` (PORT from stdout).
// Set `AI_NOTES_SKIP_BACKEND=1` to skip and point the webview to Vite / external URL only.

#[cfg(windows)]
mod win_job;

use tauri::Manager;

use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

struct BackendState {
    port: Arc<Mutex<Option<u16>>>,
    _child: Option<Child>,
    #[cfg(windows)]
    _kill_tree_job: Option<win_job::KillJobOnClose>,
}

impl Drop for BackendState {
    fn drop(&mut self) {
        #[cfg(windows)]
        {
            let had_job = self._kill_tree_job.is_some();
            // Закрытие job handle завершает всё дерево (uv, python, uvicorn, reloader).
            drop(self._kill_tree_job.take());
            if !had_job {
                if let Some(c) = self._child.as_mut() {
                    let _ = c.kill();
                }
            }
        }
        #[cfg(not(windows))]
        if let Some(c) = self._child.as_mut() {
            let _ = c.kill();
        }
        if let Some(mut c) = self._child.take() {
            let _ = c.wait();
        }
    }
}

#[tauri::command]
fn get_backend_port(state: tauri::State<'_, Arc<BackendState>>) -> Result<u16, String> {
    let start = Instant::now();
    while start.elapsed() < Duration::from_secs(30) {
        {
            let g = state.port.lock().map_err(|e| e.to_string())?;
            if let Some(p) = *g {
                return Ok(p);
            }
        }
        thread::sleep(Duration::from_millis(100));
    }
    Err("Backend port not available (is `uv` on PATH? Set AI_NOTES_SKIP_BACKEND=1 to run API manually).".into())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            if std::env::var("AI_NOTES_SKIP_BACKEND")
                .map(|s| s == "1" || s.eq_ignore_ascii_case("true"))
                .unwrap_or(false)
            {
                app.manage(Arc::new(BackendState {
                    port: Arc::new(Mutex::new(Some(8765))),
                    _child: None,
                    #[cfg(windows)]
                    _kill_tree_job: None,
                }));
                return Ok(());
            }
            let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
            // CARGO_MANIFEST_DIR = desktop/src-tauri — repo `backend` is two levels up, not under desktop/
            let backend_dir = manifest_dir.join("..").join("..").join("backend");
            let port_cell: Arc<Mutex<Option<u16>>> = Arc::new(Mutex::new(None));
            let port_for_thread = port_cell.clone();
            let mut child = match Command::new("uv")
                .arg("run")
                .arg("python")
                .arg("-m")
                .arg("ai_notes")
                .env("PORT", "0")
                .current_dir(&backend_dir)
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
            {
                Ok(c) => c,
                Err(e) => {
                    log::error!("uv spawn failed: {e}. Set AI_NOTES_SKIP_BACKEND=1 to run the API yourself.");
                    app.manage(Arc::new(BackendState {
                        port: Arc::new(Mutex::new(Some(8765))),
                        _child: None,
                        #[cfg(windows)]
                        _kill_tree_job: None,
                    }));
                    return Ok(());
                }
            };
            #[cfg(windows)]
            let kill_tree_job = match win_job::create_kill_tree_job() {
                Ok(job) => match win_job::assign_child(&job, &child) {
                    Ok(()) => Some(job),
                    Err(e) => {
                        log::warn!(
                            "AssignProcessToJobObject failed: {e}. Child processes may outlive the app."
                        );
                        None
                    }
                },
                Err(e) => {
                    log::warn!("CreateJobObject failed: {e}. Falling back to killing root uv only.");
                    None
                }
            };
            let out = child.stdout.take().expect("uv backend stdout should be piped");
            thread::spawn(move || {
                let r = BufReader::new(out);
                for line in r.lines().map_while(Result::ok) {
                    if let Some(rest) = line.strip_prefix("PORT=") {
                        if let Ok(p) = rest.trim().parse::<u16>() {
                            if let Ok(mut g) = port_for_thread.lock() {
                                *g = Some(p);
                            }
                            break;
                        }
                    }
                }
            });
            app.manage(Arc::new(BackendState {
                port: port_cell,
                _child: Some(child),
                #[cfg(windows)]
                _kill_tree_job: kill_tree_job,
            }));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_backend_port])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
