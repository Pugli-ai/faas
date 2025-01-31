"use strict";

// Function to toggle sections with animation
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const toggle = document.getElementById(`toggle-${sectionId}`);
    
    if (!section || !toggle) return;

    // Toggle the section
    if (section.classList.contains('show')) {
        section.classList.remove('show');
        toggle.classList.remove('active');
    } else {
        section.classList.add('show');
        toggle.classList.add('active');
    }

    // Update icon rotation
    const icon = toggle.querySelector('.toggle-icon');
    if (icon) {
        icon.style.transform = section.classList.contains('show') ? 'rotate(90deg)' : 'rotate(0deg)';
    }
}

// Initialize all sections
document.addEventListener('DOMContentLoaded', function() {
    // Find all section toggles
    const toggles = document.querySelectorAll('.section-toggle');
    
    // Initialize each toggle
    toggles.forEach(toggle => {
        const sectionId = toggle.getAttribute('data-section');
        if (sectionId) {
            const section = document.getElementById(sectionId);
            if (section && section.classList.contains('show')) {
                toggle.classList.add('active');
                const icon = toggle.querySelector('.toggle-icon');
                if (icon) {
                    icon.style.transform = 'rotate(90deg)';
                }
            }
        }
    });

    // Initialize tab transitions
    const tabLinks = document.querySelectorAll('.nav-link[data-bs-toggle="tab"]');
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('shown.bs.tab', function (e) {
            const target = document.querySelector(e.target.getAttribute('href'));
            if (target) {
                target.style.opacity = '1';
            }
        });
    });
});
