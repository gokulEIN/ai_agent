// Main JavaScript for AI Resume Screening System

document.addEventListener('DOMContentLoaded', function() {
    // Form submission loading state
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                form.classList.add('form-submitting');
            }
        });
    });

    // File upload preview
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileInfo = document.createElement('div');
                fileInfo.className = 'mt-2 p-2 bg-light border rounded';
                fileInfo.innerHTML = `
                    <small>
                        <i class="fas fa-file me-1"></i>
                        <strong>${file.name}</strong> 
                        (${(file.size / 1024 / 1024).toFixed(2)} MB)
                    </small>
                `;
                
                // Remove existing file info
                const existingInfo = fileInput.parentNode.querySelector('.mt-2.p-2.bg-light');
                if (existingInfo) {
                    existingInfo.remove();
                }
                
                fileInput.parentNode.appendChild(fileInfo);
            }
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.style.transition = 'opacity 0.5s';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }, 5000);
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancements
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });

    function validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        
        // Remove existing validation classes
        field.classList.remove('is-valid', 'is-invalid');
        
        if (isRequired && !value) {
            field.classList.add('is-invalid');
            return false;
        }
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                field.classList.add('is-invalid');
                return false;
            }
        }
        
        // Phone validation
        if (field.name === 'phone' && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
                field.classList.add('is-invalid');
                return false;
            }
        }
        
        if (value || !isRequired) {
            field.classList.add('is-valid');
        }
        
        return true;
    }

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.innerHTML = `<span class="char-count">0</span>/${maxLength} characters`;
        
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            const countSpan = counter.querySelector('.char-count');
            countSpan.textContent = currentLength;
            
            if (currentLength > maxLength * 0.9) {
                countSpan.style.color = '#dc3545';
            } else if (currentLength > maxLength * 0.7) {
                countSpan.style.color = '#fd7e14';
            } else {
                countSpan.style.color = '#6c757d';
            }
        });
    });

    // Progress bar for file uploads
    const uploadForms = document.querySelectorAll('form[enctype="multipart/form-data"]');
    uploadForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fileInput = form.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length > 0) {
                showUploadProgress();
            }
        });
    });

    function showUploadProgress() {
        const progressHtml = `
            <div class="upload-progress mt-3">
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 0%"></div>
                </div>
                <small class="text-muted mt-1 d-block">Uploading and processing your resume...</small>
            </div>
        `;
        
        const submitBtn = document.querySelector('input[type="submit"]');
        if (submitBtn) {
            submitBtn.insertAdjacentHTML('beforebegin', progressHtml);
            
            // Simulate progress
            const progressBar = document.querySelector('.progress-bar');
            let width = 0;
            const interval = setInterval(() => {
                width += Math.random() * 15;
                if (width > 90) width = 90;
                progressBar.style.width = width + '%';
            }, 200);
            
            // Clear interval when form actually submits
            setTimeout(() => clearInterval(interval), 5000);
        }
    }

    // Tooltips initialization (if Bootstrap tooltips are needed)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Utility functions
function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
