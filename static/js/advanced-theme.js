// Advanced Theme JavaScript for Department Inventory System

class AdvancedTheme {
  constructor() {
    this.init();
    this.bindEvents();
    this.initThemeToggle();
    this.initSidebar();
    this.initAnimations();
    this.initTooltips();
    this.initCharts();
  }

  init() {
    // Set initial theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    
    // Add loading class to body initially
    document.body.classList.add('loading');
    
    // Remove loading class after DOM is ready
    window.addEventListener('load', () => {
      setTimeout(() => {
        document.body.classList.remove('loading');
      }, 500);
    });
  }

  bindEvents() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
      setTimeout(() => {
        if (alert && alert.parentNode) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateY(-10px)';
          setTimeout(() => {
            alert.remove();
          }, 300);
        }
      }, 5000);
    });

    // Enhanced form validation
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', (e) => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.innerHTML = '<i class="bi bi-arrow-clockwise spin me-2"></i>Processing...';
          submitBtn.disabled = true;
        }
      });
    });

    // Table row hover effects
    document.querySelectorAll('.table tbody tr').forEach(row => {
      row.addEventListener('mouseenter', () => {
        row.style.transform = 'scale(1.02)';
        row.style.transition = 'transform 0.15s ease';
      });
      
      row.addEventListener('mouseleave', () => {
        row.style.transform = 'scale(1)';
      });
    });
  }

  initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-bs-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      // Add transition class
      document.documentElement.style.transition = 'all 0.3s ease';
      
      // Change theme
      document.documentElement.setAttribute('data-bs-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      
      // Update icon
      const icon = themeToggle.querySelector('i');
      icon.className = newTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
      
      // Remove transition after change
      setTimeout(() => {
        document.documentElement.style.transition = '';
      }, 300);
      
      // Trigger animation
      themeToggle.style.transform = 'rotate(360deg)';
      setTimeout(() => {
        themeToggle.style.transform = '';
      }, 300);
    });
  }

  initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');

    if (!sidebar || !mainContent) return;

    // Desktop sidebar toggle
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('sidebar-collapsed');
        
        // Save state
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
      });
    }

    // Mobile sidebar toggle
    if (mobileSidebarToggle) {
      mobileSidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('show');
      });
    }

    // Restore sidebar state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed && window.innerWidth > 768) {
      sidebar.classList.add('collapsed');
      mainContent.classList.add('sidebar-collapsed');
    }

    // Close mobile sidebar when clicking outside
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 && 
          sidebar.classList.contains('show') && 
          !sidebar.contains(e.target) && 
          e.target !== mobileSidebarToggle) {
        sidebar.classList.remove('show');
      }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        sidebar.classList.remove('show');
      }
    });

    // Add active class to current page nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
      if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
      }
    });
  }

  initAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe cards and other elements
    document.querySelectorAll('.card, .stats-card, .table').forEach(el => {
      observer.observe(el);
    });

    // Add stagger animation to cards
    document.querySelectorAll('.stats-grid .stats-card').forEach((card, index) => {
      card.style.animationDelay = `${index * 0.1}s`;
      card.classList.add('slide-up');
    });

    // Animate counters in stats cards
    this.animateCounters();
  }

  animateCounters() {
    document.querySelectorAll('.stats-value').forEach(counter => {
      const target = parseInt(counter.textContent.replace(/\D/g, ''));
      if (isNaN(target)) return;

      let current = 0;
      const increment = target / 30; // Animate over 30 frames
      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          counter.textContent = target.toLocaleString();
          clearInterval(timer);
        } else {
          counter.textContent = Math.floor(current).toLocaleString();
        }
      }, 16); // ~60fps
    });
  }

  initTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
    });
  }

  initCharts() {
    // Initialize Chart.js charts if the library is available
    if (typeof Chart !== 'undefined') {
      this.createDashboardCharts();
    }
  }

  createDashboardCharts() {
    // Example: Create a simple chart for dashboard
    const chartCanvas = document.getElementById('dashboardChart');
    if (!chartCanvas) return;

    const ctx = chartCanvas.getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['In Stock', 'Low Stock', 'Out of Stock'],
        datasets: [{
          data: [70, 20, 10],
          backgroundColor: [
            'rgb(34, 197, 94)',
            'rgb(245, 158, 11)',
            'rgb(239, 68, 68)'
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true
            }
          }
        }
      }
    });
  }

  // Utility methods
  showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.innerHTML = `
      <i class="bi bi-info-circle me-2"></i>
      ${message}
      <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      min-width: 300px;
      animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, duration);
  }

  showModal(title, content, actions = []) {
    const modalId = 'dynamicModal_' + Date.now();
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div class="modal fade" id="${modalId}" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">${title}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              ${content}
            </div>
            <div class="modal-footer">
              ${actions.map(action => 
                `<button type="button" class="btn btn-${action.type || 'secondary'}" 
                  onclick="${action.onclick || ''}" 
                  ${action.dismiss ? 'data-bs-dismiss="modal"' : ''}>
                  ${action.text}
                </button>`
              ).join('')}
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(document.getElementById(modalId));
    bsModal.show();

    // Remove modal from DOM when hidden
    document.getElementById(modalId).addEventListener('hidden.bs.modal', () => {
      modal.remove();
    });

    return bsModal;
  }

  updateProgress(elementId, percentage) {
    const progressBar = document.querySelector(`#${elementId} .progress-bar`);
    if (progressBar) {
      progressBar.style.width = `${percentage}%`;
      progressBar.setAttribute('aria-valuenow', percentage);
      progressBar.textContent = `${percentage}%`;
    }
  }
}

// CSS for additional animations
const additionalStyles = `
  <style>
    .spin {
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
    
    .notification-toast {
      animation: slideInRight 0.3s ease;
    }
    
    .hover-lift {
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .hover-lift:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .pulse {
      animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }
    
    .glow {
      animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
      from { box-shadow: 0 0 5px rgba(59, 130, 246, 0.4); }
      to { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); }
    }
  </style>
`;

// Initialize theme when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // Add additional styles
  document.head.insertAdjacentHTML('beforeend', additionalStyles);
  
  // Initialize advanced theme
  window.advancedTheme = new AdvancedTheme();
});

// Export for use in other scripts
window.AdvancedTheme = AdvancedTheme;
