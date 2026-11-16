/* ==================================================
   PROFILE CONTROLLER (profile.js)
   Read-only view, Edit Mode, Save Mode, Cancel Mode
   ================================================== */

document.addEventListener('DOMContentLoaded', () => {
  setupProfileView();
});

function setupProfileView() {
  const editBtn = document.getElementById('editProfileBtn');
  const saveBtn = document.getElementById('saveProfileBtn');
  const cancelBtn = document.getElementById('cancelProfileBtn');
  const form = document.getElementById('profileForm');

  if (!editBtn || !saveBtn || !cancelBtn || !form) return;

  // Load existing profile values
  populateProfileForm();

  editBtn.addEventListener('click', () => {
    toggleProfileEditMode(true);
  });

  cancelBtn.addEventListener('click', () => {
    populateProfileForm();
    toggleProfileEditMode(false);
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('profName').value.trim();
    const student_id = document.getElementById('profStudentId').value.trim();
    const age = document.getElementById('profAge').value.trim();
    const college = document.getElementById('profCollege').value.trim();
    const department = document.getElementById('profDepartment').value.trim();
    const course = document.getElementById('profCourse').value.trim();
    const academic_year = document.getElementById('profAcademicYear').value.trim();
    const phone = document.getElementById('profPhone').value.trim();
    const city = document.getElementById('profCity').value.trim();
    const bio = document.getElementById('profBio').value.trim();

    const payload = {
      name,
      profile: {
        student_id, age, college, department, course, academic_year, phone, city, bio
      }
    };

    try {
      const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        showToast(data.error || 'Failed to update profile.', 'error');
        return;
      }

      currentStudentProfile = data.user;
      populateProfileForm();
      toggleProfileEditMode(false);
      showToast('Profile updated successfully!', 'success');

      // Update sidebar & top bar displays
      const nameEls = document.querySelectorAll('.user-name-display');
      nameEls.forEach(el => el.textContent = data.user.name);

    } catch (err) {
      console.error(err);
      showToast('Error updating profile.', 'error');
    }
  });
}

function populateProfileForm() {
  if (!currentStudentProfile) return;

  const user = currentStudentProfile;
  const p = user.profile || {};

  setInputValue('profName', user.name || '');
  setInputValue('profEmail', user.email || '');
  setInputValue('profStudentId', p.student_id || '');
  setInputValue('profAge', p.age || '');
  setInputValue('profCollege', p.college || '');
  setInputValue('profDepartment', p.department || '');
  setInputValue('profCourse', p.course || '');
  setInputValue('profAcademicYear', p.academic_year || '');
  setInputValue('profPhone', p.phone || '');
  setInputValue('profCity', p.city || '');
  setInputValue('profBio', p.bio || '');
}

function setInputValue(id, val) {
  const el = document.getElementById(id);
  if (el) el.value = val;
}

function toggleProfileEditMode(isEditing) {
  const inputs = document.querySelectorAll('#profileForm input, #profileForm textarea');
  inputs.forEach(input => {
    if (input.id !== 'profEmail') { // Keep email read-only
      input.disabled = !isEditing;
      if (isEditing) {
        input.classList.add('bg-white', 'border-blue-500');
        input.classList.remove('bg-slate-50');
      } else {
        input.classList.remove('bg-white', 'border-blue-500');
        input.classList.add('bg-slate-50');
      }
    }
  });

  const editBtn = document.getElementById('editProfileBtn');
  const actionGroup = document.getElementById('profileActionGroup');

  if (isEditing) {
    if (editBtn) editBtn.classList.add('hidden');
    if (actionGroup) actionGroup.classList.remove('hidden');
  } else {
    if (editBtn) editBtn.classList.remove('hidden');
    if (actionGroup) actionGroup.classList.add('hidden');
  }
}
