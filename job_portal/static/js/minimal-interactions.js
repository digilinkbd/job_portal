// Enhanced Interactive Elements - FULLY FIXED VERSION
document.addEventListener('DOMContentLoaded', function() {
    
    // Add smooth loading effect to the page
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease';
    
    window.addEventListener('load', function() {
        document.body.style.opacity = '1';
    });
    
    // Enhance form submissions with loading state
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                submitBtn.disabled = true;
                
                setTimeout(function() {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
    
    // Add click effect to buttons
    document.querySelectorAll('.btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // FIXED: Handle all problematic anchor links
    document.querySelectorAll('a').forEach(function(anchor) {
        const href = anchor.getAttribute('href');
        
        // Handle all problematic anchor types
        if (href === '#' || href === '' || href === 'javascript:void(0)' || !href) {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Prevented navigation for empty link');
                
                // If it's in the navbar or a button-like element, show appropriate message
                if (this.closest('.navbar') || this.classList.contains('btn')) {
                    showToast('🚧 Feature coming soon!', 'info');
                }
            });
        } else if (href.startsWith('#') && href.length > 1) {
            // Handle valid anchor links
            anchor.addEventListener('click', function (e) {
                try {
                    const target = document.querySelector(href);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                } catch (error) {
                    console.log('Invalid selector for anchor:', href);
                    e.preventDefault();
                }
            });
        }
    });
    
    // Add animation to cards when they come into view
    function animateOnScroll() {
        const cards = document.querySelectorAll('.card');
        const windowHeight = window.innerHeight;
        
        cards.forEach(function(card) {
            const cardTop = card.getBoundingClientRect().top;
            
            if (cardTop < windowHeight - 100) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Initialize card animations
    document.querySelectorAll('.card').forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Run animation on scroll and page load
    window.addEventListener('scroll', animateOnScroll);
    setTimeout(animateOnScroll, 500);

    // Toast notification system
    function showToast(message, type = 'success') {
        document.querySelectorAll('.toast-notification').forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        
        const iconClass = type === 'success' ? 'check-circle' : type === 'info' ? 'info-circle' : 'exclamation-triangle';
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${iconClass}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Toast styles
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: 'white',
            borderRadius: '15px',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
            padding: '1rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            minWidth: '300px',
            maxWidth: '400px',
            zIndex: '10000',
            transform: 'translateX(400px)',
            transition: 'transform 0.3s ease',
            borderLeft: `4px solid ${type === 'success' ? '#10b981' : type === 'info' ? '#06b6d4' : '#f59e0b'}`
        });
        
        // Toast content styles
        const toastContent = toast.querySelector('.toast-content');
        Object.assign(toastContent.style, {
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            flex: '1'
        });
        
        // Icon color
        const icon = toast.querySelector('.fas');
        icon.style.color = type === 'success' ? '#10b981' : type === 'info' ? '#06b6d4' : '#f59e0b';
        
        // Close button
        const closeBtn = toast.querySelector('.toast-close');
        Object.assign(closeBtn.style, {
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#6b7280',
            padding: '0.25rem',
            fontSize: '0.9rem'
        });
        
        closeBtn.addEventListener('click', function() {
            toast.remove();
        });
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            if (document.body.contains(toast)) {
                toast.style.transform = 'translateX(400px)';
                setTimeout(() => toast.remove(), 300);
            }
        }, 4000);
    }

    // Make showToast globally available
    window.showToast = showToast;

    // Handle category links globally
    function fixCategoryLinks() {
        document.querySelectorAll('a[href*="category="]').forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const url = this.href;
                const categoryMatch = url.match(/category=([^&]+)/);
                const category = categoryMatch ? categoryMatch[1] : 'unknown';
                
                showToast(`🏷️ "${category}" category coming soon!`, 'info');
            });
        });
    }

    // Enhanced search functionality
    function setupEnhancedSearch() {
        const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"], input[name="q"]');
        
        searchInputs.forEach(function(input) {
            input.addEventListener('focus', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 8px 25px rgba(59, 130, 246, 0.15)';
                showToast('💡 Start typing to search for jobs!', 'info');
            });
            
            input.addEventListener('blur', function() {
                this.style.transform = '';
                this.style.boxShadow = '';
            });
            
            input.addEventListener('input', function() {
                if (this.value.length === 3) {
                    showToast('🔍 Great! Keep typing to refine your search', 'success');
                }
            });
        });
        
        // Add toast to buttons
        document.querySelectorAll('.btn-primary, .btn-warning').forEach(function(btn) {
            if (!btn.classList.contains('toast-added')) {
                btn.classList.add('toast-added');
                btn.addEventListener('click', function(e) {
                    if (this.type !== 'submit') {
                        showToast('✨ Button clicked! Nice interaction!', 'success');
                    }
                });
            }
        });
        
        // FULLY FIXED: Add ripple effect to cards without navigation errors
        document.querySelectorAll('.card').forEach(function(card) {
            if (!card.classList.contains('enhanced')) {
                card.classList.add('enhanced');
                
                // Add ripple effect on click
                card.addEventListener('click', function(e) {
                    // Check if clicked element is a link or inside a link
                    const clickedLink = e.target.closest('a');
                    
                    if (clickedLink) {
                        // If it's a link, check if it's a valid link
                        const href = clickedLink.getAttribute('href');
                        if (href && href !== '#' && href !== 'javascript:void(0)' && !href.startsWith('?category=')) {
                            // Let valid links work normally
                            return;
                        } else {
                            // Prevent invalid links from navigating
                            e.preventDefault();
                            e.stopPropagation();
                            showToast('🔗 Link functionality coming soon!', 'info');
                        }
                    } else {
                        // Clicked on card but not on a link
                        e.preventDefault();
                        e.stopPropagation();
                        showToast('📋 Job card clicked! Loading details...', 'info');
                    }
                    
                    // Always create ripple effect for any card click
                    const rect = this.getBoundingClientRect();
                    const ripple = document.createElement('div');
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;

                    Object.assign(ripple.style, {
                        position: 'absolute',
                        width: size + 'px',
                        height: size + 'px',
                        left: x + 'px',
                        top: y + 'px',
                        background: 'rgba(59, 130, 246, 0.3)',
                        borderRadius: '50%',
                        transform: 'scale(0)',
                        animation: 'ripple 0.6s ease-out',
                        pointerEvents: 'none',
                        zIndex: '10'
                    });

                    // Ensure card can contain the ripple
                    if (getComputedStyle(this).position === 'static') {
                        this.style.position = 'relative';
                    }
                    this.style.overflow = 'hidden';
                    this.appendChild(ripple);

                    setTimeout(() => {
                        if (ripple.parentNode) {
                            ripple.remove();
                        }
                    }, 600);
                });
                
                // Also prevent clicks on category links specifically
                card.querySelectorAll('a[href*="category="]').forEach(function(categoryLink) {
                    categoryLink.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        const category = this.href.split('category=')[1];
                        showToast(`🏷️ Category "${category}" coming soon!`, 'info');
                    });
                });
            }
        });
    }

    // Floating Action Button
    function setupFloatingActionButton() {
        // Remove existing FAB
        const existingFab = document.querySelector('.fab');
        if (existingFab) {
            existingFab.remove();
        }
        
        // Create new FAB
        const fab = document.createElement('button');
        fab.className = 'fab';
        fab.innerHTML = '<i class="fas fa-plus"></i>';
        fab.title = 'Quick Actions';
        
        // FAB styles
        Object.assign(fab.style, {
            position: 'fixed',
            bottom: '2rem',
            right: '2rem',
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'linear-gradient(45deg, #3b82f6, #2563eb)',
            color: 'white',
            border: 'none',
            boxShadow: '0 8px 25px rgba(59, 130, 246, 0.4)',
            fontSize: '1.5rem',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            zIndex: '1000',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        });
        
        document.body.appendChild(fab);

        // FAB click handler
        fab.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            showToast('🚀 Opening quick actions...', 'info');
            showQuickActionMenu();
        });

        // Scroll hide/show
        let lastScrollTop = 0;
        let ticking = false;
        
        function updateFabVisibility() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 300) {
                // Scrolling down
                fab.style.transform = 'translateY(100px)';
                fab.style.opacity = '0';
            } else if (scrollTop < lastScrollTop) {
                // Scrolling up
                fab.style.transform = 'translateY(0)';
                fab.style.opacity = '1';
            }
            
            lastScrollTop = scrollTop;
            ticking = false;
        }
        
        window.addEventListener('scroll', function() {
            if (!ticking) {
                requestAnimationFrame(updateFabVisibility);
                ticking = true;
            }
        });
    }

    // Quick Action Menu
    function showQuickActionMenu() {
        // Remove existing menu
        const existingMenu = document.querySelector('.quick-action-menu');
        if (existingMenu) {
            existingMenu.remove();
        }
        
        const actions = [
            { 
                icon: 'fas fa-search', 
                text: 'Search Jobs', 
                action: () => {
                    const searchInput = document.querySelector('input[name="search"], input[name="q"]');
                    if (searchInput) {
                        searchInput.focus();
                        showToast('🔍 Search focused! Start typing...', 'info');
                    } else {
                        showToast('🔍 No search box found on this page', 'info');
                    }
                }
            },
            { 
                icon: 'fas fa-bookmark', 
                text: 'Saved Jobs', 
                action: () => showToast('📚 Saved jobs feature coming soon!', 'info')
            },
            { 
                icon: 'fas fa-user', 
                text: 'Profile', 
                action: () => showToast('👤 Profile page coming soon!', 'info')
            },
            { 
                icon: 'fas fa-bell', 
                text: 'Notifications', 
                action: () => showToast('🔔 You have 3 new job alerts!', 'success')
            }
        ];

        const menu = document.createElement('div');
        menu.className = 'quick-action-menu';
        
        // Create menu HTML
        menu.innerHTML = actions.map((action, index) => `
            <div class="quick-action-item" data-index="${index}">
                <i class="${action.icon}"></i>
                <span>${action.text}</span>
            </div>
        `).join('');

        // Menu styles
        Object.assign(menu.style, {
            position: 'fixed',
            bottom: '90px',
            right: '2rem',
            background: 'white',
            borderRadius: '15px',
            boxShadow: '0 15px 35px rgba(0, 0, 0, 0.2)',
            padding: '1rem',
            zIndex: '10001',
            opacity: '0',
            transform: 'translateY(20px) scale(0.9)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            minWidth: '200px',
            border: '1px solid rgba(0, 0, 0, 0.1)'
        });

        document.body.appendChild(menu);

        // Animate menu in
        setTimeout(() => {
            menu.style.opacity = '1';
            menu.style.transform = 'translateY(0) scale(1)';
        }, 10);

        // Style and add handlers to action items
        menu.querySelectorAll('.quick-action-item').forEach((item, index) => {
            Object.assign(item.style, {
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                marginBottom: index < actions.length - 1 ? '0.5rem' : '0',
                fontSize: '0.95rem',
                color: '#374151'
            });

            // Hover effects
            item.addEventListener('mouseenter', function() {
                this.style.background = '#f3f4f6';
                this.style.transform = 'translateX(5px)';
                this.style.color = '#3b82f6';
            });

            item.addEventListener('mouseleave', function() {
                this.style.background = 'transparent';
                this.style.transform = 'translateX(0)';
                this.style.color = '#374151';
            });

            // Click handler
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const actionIndex = parseInt(this.getAttribute('data-index'));
                const action = actions[actionIndex];
                
                if (action && action.action) {
                    action.action();
                }
                
                // Close menu with animation
                menu.style.opacity = '0';
                menu.style.transform = 'translateY(20px) scale(0.9)';
                setTimeout(() => {
                    if (document.body.contains(menu)) {
                        menu.remove();
                    }
                }, 300);
            });
        });

        // Close menu when clicking outside
        setTimeout(() => {
            function closeMenu(e) {
                if (!menu.contains(e.target) && !e.target.closest('.fab')) {
                    menu.style.opacity = '0';
                    menu.style.transform = 'translateY(20px) scale(0.9)';
                    setTimeout(() => {
                        if (document.body.contains(menu)) {
                            menu.remove();
                        }
                    }, 300);
                    document.removeEventListener('click', closeMenu);
                    document.removeEventListener('touchstart', closeMenu);
                }
            }
            
            document.addEventListener('click', closeMenu);
            document.addEventListener('touchstart', closeMenu);
        }, 100);
    }

    // Initialize all features
    setupEnhancedSearch();
    setupFloatingActionButton();
    fixCategoryLinks();

    // Easter egg
    let clickCount = 0;
    document.addEventListener('click', function() {
        clickCount++;
        if (clickCount === 50) {
            showToast('🎉 Wow! You\'re really exploring this site!', 'success');
        }
    });

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            from {
                transform: scale(0);
                opacity: 1;
            }
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .fab:hover {
            transform: translateY(-3px) scale(1.1) !important;
            box-shadow: 0 12px 35px rgba(59, 130, 246, 0.6) !important;
        }
    `;
    document.head.appendChild(style);

    // Success message
    setTimeout(() => {
        showToast('🚀 All features fully loaded and working!', 'success');
    }, 2000);
});

    // Particle Background System
    function createParticleBackground() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'particle-background';
        document.body.appendChild(particleContainer);

        function createParticle() {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            const size = Math.random() * 5 + 2;
            const hue = Math.random() * 60 + 200; // Blue to cyan range
            
            Object.assign(particle.style, {
                width: size + 'px',
                height: size + 'px',
                left: Math.random() * 100 + '%',
                background: `hsl(${hue}, 70%, 60%)`,
                animationDuration: (Math.random() * 10 + 10) + 's',
                animationDelay: Math.random() * 5 + 's'
            });
            
            particleContainer.appendChild(particle);
            
            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.remove();
                }
            }, 25000);
        }

        // Create initial particles
        for (let i = 0; i < 20; i++) {
            setTimeout(() => createParticle(), i * 500);
        }

        // Continuously create new particles
        setInterval(createParticle, 2000);
    }

    // Advanced Statistics Counter with Charts
    function initializeAdvancedStats() {
        function animateCounterAdvanced(element, target, duration = 2000) {
            let current = 0;
            const increment = target / (duration / 16);
            let hasDecimal = target % 1 !== 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                if (hasDecimal) {
                    element.textContent = current.toFixed(1);
                } else {
                    element.textContent = Math.floor(current).toLocaleString();
                }
            }, 16);

            // Add micro-bounce animation
            element.classList.add('micro-bounce');
            setTimeout(() => element.classList.remove('micro-bounce'), 600);
        }

        // Observe stats for animation
        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-target') || counter.textContent.replace(/[^\d.]/g, ''));
                    
                    if (target && !counter.classList.contains('animated')) {
                        counter.classList.add('animated');
                        counter.textContent = '0';
                        setTimeout(() => animateCounterAdvanced(counter, target), 200);
                    }
                }
            });
        }, { threshold: 0.5 });

        document.querySelectorAll('.stats-number, .stat-number-advanced').forEach(stat => {
            statsObserver.observe(stat);
        });
    }

    // Smart Search with Autocomplete
    function initializeSmartSearch() {
        const searchInputs = document.querySelectorAll('.search-input-smart, input[name="search"], input[name="q"]');
        
        // Mock job search data
        const searchData = [
            { title: 'Frontend Developer', type: 'job', icon: 'fas fa-code' },
            { title: 'React Developer', type: 'job', icon: 'fab fa-react' },
            { title: 'Python Developer', type: 'job', icon: 'fab fa-python' },
            { title: 'UI/UX Designer', type: 'job', icon: 'fas fa-palette' },
            { title: 'Data Scientist', type: 'job', icon: 'fas fa-chart-bar' },
            { title: 'Product Manager', type: 'job', icon: 'fas fa-tasks' },
            { title: 'DevOps Engineer', type: 'job', icon: 'fas fa-server' },
            { title: 'Mobile Developer', type: 'job', icon: 'fas fa-mobile-alt' },
            { title: 'San Francisco', type: 'location', icon: 'fas fa-map-marker-alt' },
            { title: 'New York', type: 'location', icon: 'fas fa-map-marker-alt' },
            { title: 'Remote', type: 'location', icon: 'fas fa-home' },
            { title: 'Technology', type: 'category', icon: 'fas fa-laptop' },
            { title: 'Healthcare', type: 'category', icon: 'fas fa-heartbeat' },
            { title: 'Finance', type: 'category', icon: 'fas fa-dollar-sign' }
        ];

        searchInputs.forEach(input => {
            const wrapper = input.parentNode;
            let suggestionsContainer = wrapper.querySelector('.search-suggestions');
            
            if (!suggestionsContainer) {
                suggestionsContainer = document.createElement('div');
                suggestionsContainer.className = 'search-suggestions';
                wrapper.appendChild(suggestionsContainer);
            }

            input.addEventListener('input', function() {
                const query = this.value.toLowerCase().trim();
                
                if (query.length < 2) {
                    suggestionsContainer.classList.remove('show');
                    return;
                }

                const matches = searchData.filter(item => 
                    item.title.toLowerCase().includes(query)
                ).slice(0, 5);

                if (matches.length > 0) {
                    suggestionsContainer.innerHTML = matches.map(item => `
                        <div class="suggestion-item" data-value="${item.title}">
                            <i class="${item.icon}" style="color: var(--primary-color);"></i>
                            <div>
                                <div style="font-weight: 600;">${item.title}</div>
                                <div style="font-size: 0.85rem; color: var(--gray-500);">${item.type}</div>
                            </div>
                        </div>
                    `).join('');

                    suggestionsContainer.classList.add('show');

                    // Add click handlers
                    suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
                        item.addEventListener('click', function() {
                            input.value = this.getAttribute('data-value');
                            suggestionsContainer.classList.remove('show');
                            showToast(`🔍 Selected: ${this.getAttribute('data-value')}`, 'success');
                        });
                    });
                } else {
                    suggestionsContainer.classList.remove('show');
                }
            });

            // Hide suggestions when clicking outside
            document.addEventListener('click', function(e) {
                if (!wrapper.contains(e.target)) {
                    suggestionsContainer.classList.remove('show');
                }
            });
        });
    }

    // Dark Mode Toggle
    function initializeDarkMode() {
        // Create theme toggle button
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.title = 'Toggle Dark Mode';
        document.body.appendChild(themeToggle);

        // Check for saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggle.classList.add('dark');
        }

        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            this.classList.toggle('dark');
            
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            showToast(`🌙 ${isDark ? 'Dark' : 'Light'} mode activated!`, 'success');
            
            // Add pulse effect
            this.classList.add('pulse-glow');
            setTimeout(() => this.classList.remove('pulse-glow'), 2000);
        });
    }

    // Advanced Micro-interactions
    function initializeMicroInteractions() {
        // Add hover effects to all interactive elements
        document.querySelectorAll('.btn, .card, .widget-advanced, .stat-advanced').forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transform = getComputedStyle(this).transform + ' scale(1.02)';
            });

            element.addEventListener('mouseleave', function() {
                this.style.transform = getComputedStyle(this).transform.replace(' scale(1.02)', '');
            });
        });

        // Add click animations to buttons
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function() {
                this.classList.add('micro-bounce');
                setTimeout(() => this.classList.remove('micro-bounce'), 600);
            });
        });

        // Add tooltips to elements with data-tooltip
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.classList.add('tooltip-advanced');
        });
    }

    // Advanced Loading States
    function addAdvancedLoadingStates() {
        // Add loading to all forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                this.classList.add('loading-advanced');
            });
        });

        // Add loading to navigation links
        document.querySelectorAll('a[href]').forEach(link => {
            link.addEventListener('click', function() {
                if (this.hostname === window.location.hostname) {
                    this.classList.add('loading-advanced');
                }
            });
        });
    }

    // Performance Monitor
    function initializePerformanceMonitor() {
        // Monitor page load performance
        window.addEventListener('load', function() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log(`🚀 Page loaded in ${loadTime}ms`);
            
            if (loadTime < 2000) {
                setTimeout(() => {
                    showToast('⚡ Lightning fast load time!', 'success');
                }, 1000);
            }
        });

        // Monitor memory usage (if available)
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize / memory.jsHeapSizeLimit > 0.9) {
                    console.warn('⚠️ High memory usage detected');
                }
            }, 30000);
        }
    }

    // Advanced Analytics
    function initializeAnalytics() {
        let interactionCount = 0;
        let sessionStart = Date.now();

        // Track user interactions
        ['click', 'scroll', 'keypress'].forEach(event => {
            document.addEventListener(event, function() {
                interactionCount++;
                
                // Show engagement milestone
                if (interactionCount === 100) {
                    showToast('🎉 Wow! 100 interactions! You\'re really engaged!', 'success');
                } else if (interactionCount === 500) {
                    showToast('🏆 Power user! 500 interactions achieved!', 'success');
                }
            });
        });

        // Track session duration
        setInterval(() => {
            const sessionDuration = (Date.now() - sessionStart) / 1000 / 60; // minutes
            if (sessionDuration >= 5 && sessionDuration < 5.1) {
                showToast('⏰ You\'ve been exploring for 5 minutes!', 'info');
            }
        }, 6000);
    }

    // Initialize all Step 5 features
    setTimeout(() => {
        // Only create particles on desktop for performance
        if (window.innerWidth > 768) {
            createParticleBackground();
        }
        
        initializeAdvancedStats();
        initializeSmartSearch();
        initializeDarkMode();
        initializeMicroInteractions();
        addAdvancedLoadingStates();
        initializePerformanceMonitor();
        initializeAnalytics();
        
        showToast('🌟 Ultimate features activated! Your job portal is now incredible!', 'success');
        
        // Add some celebration effects
        setTimeout(() => {
            showToast('✨ Particle effects active!', 'info');
        }, 2000);
        
        setTimeout(() => {
            showToast('🎨 Dark mode toggle available!', 'info');
        }, 4000);
        
        setTimeout(() => {
            showToast('🔍 Smart search with autocomplete ready!', 'info');
        }, 6000);
        
    }, 3000);

    // Add some fun easter eggs
    let konamiCode = [];
    const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // Up, Up, Down, Down, Left, Right, Left, Right, B, A
    
    document.addEventListener('keydown', function(e) {
        konamiCode.push(e.keyCode);
        if (konamiCode.length > konamiSequence.length) {
            konamiCode.shift();
        }
        
        if (konamiCode.join(',') === konamiSequence.join(',')) {
            showToast('🎮 Konami Code activated! You found the secret!', 'success');
            document.body.style.animation = 'rainbow 2s infinite';
            setTimeout(() => {
                document.body.style.animation = '';
            }, 5000);
        }
    });

    // Add rainbow animation for konami code
    const rainbowStyle = document.createElement('style');
    rainbowStyle.textContent = `
        @keyframes rainbow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
    `;
    document.head.appendChild(rainbowStyle);
