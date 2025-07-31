// Material Design Components JavaScript
class MaterialComponents {
  constructor() {
    this.init();
  }

  init() {
    this.initTextFields();
    this.initSelects();
    this.initTabs();
    this.initButtons();
    this.initFABs();
    this.initSnackbar();
    this.initTopAppBar();
    this.initLinearProgress();
  }

  // Initialize text fields
  initTextFields() {
    const textFields = document.querySelectorAll('.mdc-text-field');
    textFields.forEach(field => {
      const input = field.querySelector('.mdc-text-field__input');
      const label = field.querySelector('.mdc-floating-label');
      const lineRipple = field.querySelector('.mdc-line-ripple');
      const charCounter = field.querySelector('.mdc-text-field-character-counter');

      if (input && label) {
        // Handle focus/blur
        input.addEventListener('focus', () => {
          field.classList.add('mdc-text-field--focused');
          if (lineRipple) lineRipple.style.transform = 'scaleX(1)';
        });

        input.addEventListener('blur', () => {
          field.classList.remove('mdc-text-field--focused');
          if (lineRipple) lineRipple.style.transform = 'scaleX(0)';
        });

        // Handle input changes
        input.addEventListener('input', () => {
          this.updateFloatingLabel(field, input, label);
          this.updateCharacterCounter(input, charCounter);
          this.validateField(field, input);
        });

        // Initial state
        this.updateFloatingLabel(field, input, label);
        this.updateCharacterCounter(input, charCounter);
      }

      // Handle trailing icon clicks
      const trailingIcon = field.querySelector('.mdc-text-field__icon--trailing');
      if (trailingIcon) {
        trailingIcon.addEventListener('click', (e) => {
          this.handleTrailingIconClick(e, field, input);
        });
      }
    });
  }

  updateFloatingLabel(field, input, label) {
    if (input.value || input === document.activeElement) {
      field.classList.add('mdc-text-field--label-floating');
    } else {
      field.classList.remove('mdc-text-field--label-floating');
    }
  }

  updateCharacterCounter(input, counter) {
    if (counter && input.maxLength > 0) {
      counter.textContent = `${input.value.length} / ${input.maxLength}`;
    }
  }

  validateField(field, input) {
    const isRequired = field.hasAttribute('data-required') || input.hasAttribute('required');
    const isValid = input.checkValidity();

    field.classList.remove('field-error', 'field-success');
    
    if (input.value) {
      if (isValid) {
        field.classList.add('field-success');
      } else {
        field.classList.add('field-error');
      }
    } else if (isRequired) {
      field.classList.add('field-error');
    }
  }

  handleTrailingIconClick(e, field, input) {
    const icon = e.currentTarget;
    
    if (icon.classList.contains('sku-generator')) {
      this.generateSKU(input);
    }
  }

  generateSKU(input) {
    // Simple SKU generation logic
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.random().toString(36).substr(2, 4).toUpperCase();
    const sku = `PRD-${timestamp}-${random}`;
    
    input.value = sku;
    input.dispatchEvent(new Event('input'));
    
    this.showSnackbar('SKU generated successfully!');
  }

  // Initialize select components
  initSelects() {
    const selects = document.querySelectorAll('.mdc-select');
    selects.forEach(select => {
      const anchor = select.querySelector('.mdc-select__anchor');
      const menu = select.querySelector('.mdc-select__menu');
      const hiddenSelect = select.querySelector('select[style*="display: none"]');
      const selectedText = select.querySelector('.mdc-select__selected-text');
      const options = select.querySelectorAll('.mdc-deprecated-list-item[data-value]');

      if (anchor && menu) {
        // Handle anchor clicks
        anchor.addEventListener('click', () => {
          const isOpen = select.classList.contains('mdc-select--activated');
          this.closeAllSelects();
          
          if (!isOpen) {
            select.classList.add('mdc-select--activated');
            menu.style.display = 'block';
            setTimeout(() => menu.classList.add('mdc-menu-surface--open'), 10);
          }
        });

        // Handle option clicks
        options.forEach(option => {
          option.addEventListener('click', () => {
            const value = option.dataset.value;
            const text = option.textContent.trim();
            
            // Update UI
            options.forEach(opt => opt.classList.remove('mdc-deprecated-list-item--selected'));
            option.classList.add('mdc-deprecated-list-item--selected');
            selectedText.textContent = text;
            
            // Update hidden select
            if (hiddenSelect) {
              hiddenSelect.value = value;
              hiddenSelect.dispatchEvent(new Event('change'));
            }
            
            // Close menu
            this.closeSelect(select);
          });
        });

        // Set initial selection
        if (hiddenSelect && hiddenSelect.value) {
          const selectedOption = select.querySelector(`[data-value="${hiddenSelect.value}"]`);
          if (selectedOption) {
            selectedText.textContent = selectedOption.textContent.trim();
            selectedOption.classList.add('mdc-deprecated-list-item--selected');
          }
        }
      }
    });

    // Close selects when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.mdc-select')) {
        this.closeAllSelects();
      }
    });
  }

  closeSelect(select) {
    const menu = select.querySelector('.mdc-select__menu');
    if (menu) {
      menu.classList.remove('mdc-menu-surface--open');
      setTimeout(() => {
        menu.style.display = 'none';
        select.classList.remove('mdc-select--activated');
      }, 150);
    }
  }

  closeAllSelects() {
    const selects = document.querySelectorAll('.mdc-select--activated');
    selects.forEach(select => this.closeSelect(select));
  }

  // Initialize tabs
  initTabs() {
    const tabBar = document.querySelector('.mdc-tab-bar');
    if (!tabBar) return;

    const tabs = tabBar.querySelectorAll('.mdc-tab');
    const panels = document.querySelectorAll('.tab-panel');

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        // Remove active states
        tabs.forEach(t => {
          t.classList.remove('mdc-tab--active');
          t.setAttribute('aria-selected', 'false');
          t.setAttribute('tabindex', '-1');
        });
        panels.forEach(p => p.classList.remove('active'));

        // Add active state to clicked tab
        tab.classList.add('mdc-tab--active');
        tab.setAttribute('aria-selected', 'true');
        tab.setAttribute('tabindex', '0');

        // Show corresponding panel
        const tabId = tab.dataset.tab;
        const panel = document.getElementById(`${tabId}-panel`);
        if (panel) {
          panel.classList.add('active');
          this.updateProgress();
          this.updateFABs();
        }

        // Update tab indicator
        this.updateTabIndicator(tab);
      });
    });
  }

  updateTabIndicator(activeTab) {
    const tabBar = activeTab.closest('.mdc-tab-bar');
    const indicator = activeTab.querySelector('.mdc-tab-indicator');
    
    // Remove active from all indicators
    tabBar.querySelectorAll('.mdc-tab-indicator').forEach(ind => {
      ind.classList.remove('mdc-tab-indicator--active');
    });
    
    // Add active to current indicator
    if (indicator) {
      indicator.classList.add('mdc-tab-indicator--active');
    }
  }

  updateProgress() {
    const completedSections = this.getCompletedSections();
    const totalSections = document.querySelectorAll('.tab-panel').length;
    const percentage = (completedSections / totalSections) * 100;

    // Update progress bar
    const progressBar = document.querySelector('.mdc-linear-progress__primary-bar .mdc-linear-progress__bar-inner');
    if (progressBar) {
      progressBar.style.transform = `scaleX(${percentage / 100})`;
    }

    // Update progress text
    const completedText = document.querySelector('.completed-sections');
    if (completedText) {
      completedText.textContent = completedSections;
    }
  }

  getCompletedSections() {
    let completed = 0;
    const panels = document.querySelectorAll('.tab-panel');
    
    panels.forEach(panel => {
      const requiredFields = panel.querySelectorAll('[required]');
      let panelComplete = true;
      
      requiredFields.forEach(field => {
        if (!field.value || !field.checkValidity()) {
          panelComplete = false;
        }
      });
      
      if (panelComplete && requiredFields.length > 0) {
        completed++;
      }
    });
    
    return completed;
  }

  updateFABs() {
    const tabs = document.querySelectorAll('.mdc-tab');
    const activeTabIndex = Array.from(tabs).findIndex(tab => tab.classList.contains('mdc-tab--active'));
    
    const prevBtn = document.getElementById('previous-tab');
    const nextBtn = document.getElementById('next-tab');
    
    if (prevBtn) {
      if (activeTabIndex > 0) {
        prevBtn.style.display = 'flex';
      } else {
        prevBtn.style.display = 'none';
      }
    }
    
    if (nextBtn) {
      if (activeTabIndex < tabs.length - 1) {
        nextBtn.querySelector('.material-icons').textContent = 'navigate_next';
      } else {
        nextBtn.querySelector('.material-icons').textContent = 'save';
      }
    }
  }

  // Initialize buttons
  initButtons() {
    const buttons = document.querySelectorAll('.mdc-button');
    buttons.forEach(button => {
      button.addEventListener('click', (e) => {
        this.createRipple(e, button);
      });
    });
  }

  // Initialize FABs
  initFABs() {
    const prevBtn = document.getElementById('previous-tab');
    const nextBtn = document.getElementById('next-tab');
    
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        this.navigateTab(-1);
      });
    }
    
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        const tabs = document.querySelectorAll('.mdc-tab');
        const activeTabIndex = Array.from(tabs).findIndex(tab => tab.classList.contains('mdc-tab--active'));
        
        if (activeTabIndex < tabs.length - 1) {
          this.navigateTab(1);
        } else {
          // Last tab - submit form
          const form = document.getElementById('product-form');
          if (form) {
            form.submit();
          }
        }
      });
    }
  }

  navigateTab(direction) {
    const tabs = document.querySelectorAll('.mdc-tab');
    const activeTabIndex = Array.from(tabs).findIndex(tab => tab.classList.contains('mdc-tab--active'));
    const newIndex = activeTabIndex + direction;
    
    if (newIndex >= 0 && newIndex < tabs.length) {
      tabs[newIndex].click();
    }
  }

  // Initialize snackbar
  initSnackbar() {
    this.snackbar = document.getElementById('notification-snackbar');
  }

  showSnackbar(message, action = null) {
    if (!this.snackbar) return;
    
    const label = this.snackbar.querySelector('.mdc-snackbar__label');
    if (label) {
      label.textContent = message;
    }
    
    this.snackbar.classList.add('mdc-snackbar--open');
    
    // Auto-hide after 4 seconds
    setTimeout(() => {
      this.hideSnackbar();
    }, 4000);
  }

  hideSnackbar() {
    if (this.snackbar) {
      this.snackbar.classList.remove('mdc-snackbar--open');
    }
  }

  // Initialize top app bar
  initTopAppBar() {
    const topAppBar = document.querySelector('.mdc-top-app-bar');
    if (!topAppBar) return;

    // Handle scroll behavior if needed
    let lastScrollTop = 0;
    window.addEventListener('scroll', () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      
      if (scrollTop > lastScrollTop) {
        // Scrolling down
        topAppBar.style.transform = 'translateY(-100%)';
      } else {
        // Scrolling up
        topAppBar.style.transform = 'translateY(0)';
      }
      
      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    });
  }

  // Initialize linear progress
  initLinearProgress() {
    const progress = document.getElementById('form-progress');
    if (progress) {
      // Initial progress update
      setTimeout(() => {
        this.updateProgress();
      }, 100);
    }
  }

  // Utility: Create ripple effect
  createRipple(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.6);
      transform: scale(0);
      animation: ripple 600ms linear;
      left: ${x}px;
      top: ${y}px;
      width: ${size}px;
      height: ${size}px;
      pointer-events: none;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }

  // Public methods for external use
  updateTabStatus(tabId, status) {
    const tab = document.querySelector(`[data-tab="${tabId}"]`);
    if (tab) {
      const indicator = tab.querySelector('.tab-status-indicator');
      if (indicator) {
        indicator.setAttribute('data-status', status);
        const icon = indicator.querySelector('.material-icons');
        if (icon) {
          switch (status) {
            case 'complete':
              icon.textContent = 'check_circle';
              break;
            case 'error':
              icon.textContent = 'error';
              break;
            default:
              icon.textContent = 'radio_button_unchecked';
          }
        }
      }
    }
    this.updateProgress();
  }

  showLoadingOverlay() {
    const overlay = document.getElementById('form-loading-overlay');
    if (overlay) {
      overlay.style.display = 'flex';
    }
  }

  hideLoadingOverlay() {
    const overlay = document.getElementById('form-loading-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  }
}

// Add ripple animation CSS
const rippleCSS = `
@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}
`;

const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.materialComponents = new MaterialComponents();
});
