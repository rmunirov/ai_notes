//! Windows: при закрытии job handle все процессы в джобе завершаются (включая дерево uv → python → uvicorn).

use std::io;
use std::os::windows::io::AsRawHandle;
use std::process::Child;

use windows_sys::Win32::Foundation::{CloseHandle, HANDLE};
use windows_sys::Win32::System::JobObjects::{
    AssignProcessToJobObject, CreateJobObjectW, JobObjectExtendedLimitInformation,
    JOBOBJECT_BASIC_LIMIT_INFORMATION, JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
    SetInformationJobObject, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
};

/// Держит job object с `KILL_ON_JOB_CLOSE`. При `Drop` закрывается handle и ОС гасит всё дерево.
pub struct KillJobOnClose(HANDLE);

// HANDLE владеется только главным потоком приложения; для `tauri::State` нужны эти маркеры.
unsafe impl Send for KillJobOnClose {}
unsafe impl Sync for KillJobOnClose {}

impl Drop for KillJobOnClose {
    fn drop(&mut self) {
        unsafe {
            if !self.0.is_null() {
                CloseHandle(self.0);
            }
        }
    }
}

pub fn create_kill_tree_job() -> io::Result<KillJobOnClose> {
    unsafe {
        let job = CreateJobObjectW(std::ptr::null(), std::ptr::null());
        if job.is_null() {
            return Err(io::Error::last_os_error());
        }

        let mut extended: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
        extended.BasicLimitInformation = JOBOBJECT_BASIC_LIMIT_INFORMATION {
            LimitFlags: JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
            ..std::mem::zeroed()
        };

        let ok = SetInformationJobObject(
            job,
            JobObjectExtendedLimitInformation,
            std::ptr::addr_of!(extended).cast(),
            std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
        );
        if ok == 0 {
            CloseHandle(job);
            return Err(io::Error::last_os_error());
        }

        Ok(KillJobOnClose(job))
    }
}

pub fn assign_child(job: &KillJobOnClose, child: &Child) -> io::Result<()> {
    let raw = child.as_raw_handle();
    unsafe {
        if AssignProcessToJobObject(job.0, raw as HANDLE) == 0 {
            return Err(io::Error::last_os_error());
        }
    }
    Ok(())
}
