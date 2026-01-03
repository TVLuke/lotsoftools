document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const desktopCategorizedBtn = document.getElementById('desktop-categorized');
    const desktopCompactBtn = document.getElementById('desktop-compact');
    const mobileCategorizedBtn = document.getElementById('mobile-categorized');
    const mobileCompactBtn = document.getElementById('mobile-compact');
    
    function isMobileView() {
        return window.innerWidth < 768;
    }
    
    function updateLayoutForScreenSize() {
        const isMobile = isMobileView();
        const currentDesktopLayout = body.getAttribute('data-desktop-layout') || 'categorized';
        const currentMobileLayout = body.getAttribute('data-mobile-layout') || 'compact';
        
        if (isMobile) {
            body.classList.remove('compact-layout');
            
            if (currentMobileLayout === 'compact') {
                body.classList.add('compact-layout-mobile');
            } else {
                body.classList.remove('compact-layout-mobile');
            }
        } else {
            body.classList.remove('compact-layout-mobile');
            
            if (currentDesktopLayout === 'compact') {
                body.classList.add('compact-layout');
            } else {
                body.classList.remove('compact-layout');
            }
        }
    }
    
    window.addEventListener('resize', updateLayoutForScreenSize);
    
    const currentDesktopLayout = body.getAttribute('data-desktop-layout') || 'categorized';
    const currentMobileLayout = body.getAttribute('data-mobile-layout') || 'compact';
    
    updateLayoutForScreenSize();
    
    if (currentDesktopLayout === 'compact') {
        body.classList.add('compact-layout');
        if (desktopCompactBtn) desktopCompactBtn.classList.add('active');
        if (desktopCategorizedBtn) desktopCategorizedBtn.classList.remove('active');
    } else {
        body.classList.remove('compact-layout');
        if (desktopCategorizedBtn) desktopCategorizedBtn.classList.add('active');
        if (desktopCompactBtn) desktopCompactBtn.classList.remove('active');
    }
    
    if (currentMobileLayout === 'compact') {
        body.classList.add('compact-layout-mobile');
        if (mobileCompactBtn) mobileCompactBtn.classList.add('active');
        if (mobileCategorizedBtn) mobileCategorizedBtn.classList.remove('active');
    } else {
        body.classList.remove('compact-layout-mobile');
        if (mobileCategorizedBtn) mobileCategorizedBtn.classList.add('active');
        if (mobileCompactBtn) mobileCompactBtn.classList.remove('active');
    }
    
    if (desktopCategorizedBtn) {
        desktopCategorizedBtn.addEventListener('click', function() {
            setDesktopLayout('categorized');
        });
    }
    
    if (desktopCompactBtn) {
        desktopCompactBtn.addEventListener('click', function() {
            setDesktopLayout('compact');
        });
    }
    
    if (mobileCategorizedBtn) {
        mobileCategorizedBtn.addEventListener('click', function() {
            setMobileLayout('categorized');
        });
    }
    
    if (mobileCompactBtn) {
        mobileCompactBtn.addEventListener('click', function() {
            setMobileLayout('compact');
        });
    }
    
    function setDesktopLayout(layout) {
        if (layout === 'compact') {
            if (desktopCompactBtn) desktopCompactBtn.classList.add('active');
            if (desktopCategorizedBtn) desktopCategorizedBtn.classList.remove('active');
        } else {
            if (desktopCategorizedBtn) desktopCategorizedBtn.classList.add('active');
            if (desktopCompactBtn) desktopCompactBtn.classList.remove('active');
        }
        
        body.setAttribute('data-desktop-layout', layout);
        updateLayoutForScreenSize();
        
        fetch('/api/layout/desktop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ layout: layout }),
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error setting layout preference:', error);
        });
    }
    
    function setMobileLayout(layout) {
        if (layout === 'compact') {
            if (mobileCompactBtn) mobileCompactBtn.classList.add('active');
            if (mobileCategorizedBtn) mobileCategorizedBtn.classList.remove('active');
        } else {
            if (mobileCategorizedBtn) mobileCategorizedBtn.classList.add('active');
            if (mobileCompactBtn) mobileCompactBtn.classList.remove('active');
        }
        
        body.setAttribute('data-mobile-layout', layout);
        updateLayoutForScreenSize();
        
        fetch('/api/layout/mobile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ layout: layout }),
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error setting layout preference:', error);
        });
    }
});
