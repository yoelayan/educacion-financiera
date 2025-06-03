/* Project specific Javascript goes here. */

// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
  // Sidebar toggle functionality
  const sidebarToggle = document.querySelector('.sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function() {
      sidebar.classList.toggle('sidebar-collapsed');

      // Update toggle icon
      const icon = this.querySelector('i');
      if (icon) {
        if (sidebar.classList.contains('sidebar-collapsed')) {
          icon.className = 'bi bi-chevron-right';
        } else {
          icon.className = 'bi bi-chevron-left';
        }
      }
    });
  }

  // Mobile sidebar toggle
  const mobileToggle = document.querySelector('.navbar-toggler');
  const mobileSidebar = document.querySelector('.sidebar');

  if (window.innerWidth <= 768) {
    // Create mobile sidebar overlay
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      z-index: 1025;
      display: none;
    `;
    document.body.appendChild(overlay);

    // Mobile menu toggle
    if (mobileToggle) {
      mobileToggle.addEventListener('click', function() {
        if (mobileSidebar) {
          mobileSidebar.classList.toggle('show');
          overlay.style.display = mobileSidebar.classList.contains('show') ? 'block' : 'none';
          document.body.style.overflow = mobileSidebar.classList.contains('show') ? 'hidden' : '';
        }
      });
    }

    // Close sidebar when clicking overlay
    overlay.addEventListener('click', function() {
      if (mobileSidebar) {
        mobileSidebar.classList.remove('show');
        overlay.style.display = 'none';
        document.body.style.overflow = '';
      }
    });
  }

  // Search functionality
  const searchInput = document.querySelector('.search-input');
  const searchForm = document.querySelector('.search-form');

  if (searchInput) {
    // Search suggestions (placeholder functionality)
    searchInput.addEventListener('input', function() {
      const query = this.value.trim();

      if (query.length > 2) {
        // Here you would typically make an AJAX request to get suggestions
        console.log('Searching for:', query);

        // Show suggestions container if it exists
        const suggestions = document.querySelector('.search-suggestions');
        if (suggestions) {
          suggestions.style.display = 'block';
        }
      } else {
        // Hide suggestions
        const suggestions = document.querySelector('.search-suggestions');
        if (suggestions) {
          suggestions.style.display = 'none';
        }
      }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
      const searchComponent = document.querySelector('.search-component');
      const suggestions = document.querySelector('.search-suggestions');

      if (suggestions && searchComponent && !searchComponent.contains(e.target)) {
        suggestions.style.display = 'none';
      }
    });
  }

  // Course card hover effects
  const courseCards = document.querySelectorAll('.course-card, .course-progress-card, .recommended-course-card');

  courseCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-4px)';
    });

    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });

  // Smooth scrolling for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]');

  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');

      if (href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);

        if (target) {
          const offsetTop = target.offsetTop - 100; // Account for fixed navbar

          window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  // Auto-hide alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');

  alerts.forEach(alert => {
    setTimeout(() => {
      if (alert && alert.parentNode) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';

        setTimeout(() => {
          if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
          }
        }, 300);
      }
    }, 5000);
  });

  // Progress bar animations
  const progressBars = document.querySelectorAll('.progress-bar');

  const animateProgressBars = () => {
    progressBars.forEach(bar => {
      const rect = bar.getBoundingClientRect();
      const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

      if (isVisible && !bar.classList.contains('animated')) {
        bar.classList.add('animated');
        const width = bar.style.width;
        bar.style.width = '0%';

        setTimeout(() => {
          bar.style.transition = 'width 1s ease-in-out';
          bar.style.width = width;
        }, 100);
      }
    });
  };

  // Animate progress bars on scroll
  window.addEventListener('scroll', animateProgressBars);
  animateProgressBars(); // Initial check

  // Navbar scroll effect
  const navbar = document.querySelector('.navbar-custom');

  if (navbar) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 50) {
        navbar.style.backgroundColor = 'rgba(152, 202, 63, 0.95)';
        navbar.style.backdropFilter = 'blur(10px)';
      } else {
        navbar.style.backgroundColor = '';
        navbar.style.backdropFilter = '';
      }
    });
  }
});

// Utility functions
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  notification.style.cssText = `
    top: 100px;
    right: 20px;
    z-index: 1050;
    min-width: 300px;
  `;

  notification.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;

  document.body.appendChild(notification);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.classList.remove('show');
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 150);
    }
  }, 5000);
}

// Export for global use
window.showNotification = showNotification;
