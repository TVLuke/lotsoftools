document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchInputMobile = document.getElementById('searchInputMobile');
    
    function performSearch(searchTerm) {
        searchTerm = searchTerm.toLowerCase();
        
        const categories = document.querySelectorAll('.category-section');
        categories.forEach(function(category) {
            const links = category.querySelectorAll('.col');
            let visibleLinks = 0;
            
            links.forEach(function(link) {
                const linkName = link.querySelector('.tile-title').textContent.toLowerCase();
                const linkDescription = link.querySelector('.tile-description');
                const description = linkDescription ? linkDescription.textContent.toLowerCase() : '';
                
                if (linkName.includes(searchTerm) || description.includes(searchTerm)) {
                    link.style.display = '';
                    visibleLinks++;
                } else {
                    link.style.display = 'none';
                }
            });
            
            if (visibleLinks === 0) {
                category.style.display = 'none';
            } else {
                category.style.display = '';
            }
        });
        
        const compactContainer = document.querySelector('.compact-tiles');
        if (compactContainer) {
            const compactLinks = compactContainer.querySelectorAll('.col');
            
            compactLinks.forEach(function(link) {
                const linkName = link.querySelector('.tile-title').textContent.toLowerCase();
                const linkDescription = link.querySelector('.tile-description');
                const description = linkDescription ? linkDescription.textContent.toLowerCase() : '';
                
                if (linkName.includes(searchTerm) || description.includes(searchTerm)) {
                    link.style.display = '';
                } else {
                    link.style.display = 'none';
                }
            });
        }
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            if (searchInputMobile) searchInputMobile.value = this.value;
            performSearch(this.value);
        });
    }
    
    if (searchInputMobile) {
        searchInputMobile.addEventListener('input', function() {
            if (searchInput) searchInput.value = this.value;
            performSearch(this.value);
        });
    }
});
