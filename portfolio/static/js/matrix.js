// Matrix Animation with smooth page transitions
let matrixInstance = null;

class MatrixAnimation {
    constructor() {
        if (matrixInstance) {
            return matrixInstance;
        }
        matrixInstance = this;
        
        this.canvas = document.getElementById('matrix-background');
        this.ctx = this.canvas.getContext('2d');
        this.characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,.<>?/~`';
        this.fontSize = 14;
        this.drops = [];
        this.isAnimating = true;
        this.normalSpeed = 1;
        this.boostSpeed = 3;
        this.currentSpeed = this.normalSpeed;
        this.boostDuration = 1000;
        this.isBoostActive = false;
        this.transitionSpeed = 2;

        this.initCanvas();
        this.setupEventListeners();
        this.animate();
    }

    initCanvas() {
        this.setCanvasSize();
        this.ctx.font = `${this.fontSize}px 'Courier New', monospace`;
        this.resetDrops();
    }

    setCanvasSize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    resetDrops() {
        const columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = Array(columns).fill(1);
    }

    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => {
            this.setCanvasSize();
            this.resetDrops();
        });

        // Handle page visibility
        document.addEventListener('visibilitychange', () => {
            this.isAnimating = !document.hidden;
            if (this.isAnimating) this.animate();
        });

        // Handle link clicks with transition effect
        document.addEventListener('click', (e) => {
            const clickedLink = e.target.closest('a');
            if (clickedLink && !e.ctrlKey && !e.shiftKey && !e.metaKey) {
                e.preventDefault();
                this.handlePageTransition(clickedLink.href);
            }
        });

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.activateSpeedBoost();
        });
    }

    handlePageTransition(url) {
        // Activate speed boost for transition
        this.activateSpeedBoost();

        // Add transition class to body
        document.body.classList.add('page-transitioning');

        // Fetch new page content
        fetch(url)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const newDoc = parser.parseFromString(html, 'text/html');
                
                // Update main content
                const currentMain = document.querySelector('main');
                const newMain = newDoc.querySelector('main');
                if (currentMain && newMain) {
                    currentMain.innerHTML = newMain.innerHTML;
                }

                // Update page title
                document.title = newDoc.title;

                // Update URL
                window.history.pushState({}, '', url);

                // Remove transition class
                setTimeout(() => {
                    document.body.classList.remove('page-transitioning');
                }, 300);
            })
            .catch(() => window.location.href = url); // Fallback to normal navigation
    }

    activateSpeedBoost() {
        if (!this.isBoostActive) {
            this.isBoostActive = true;
            this.currentSpeed = this.boostSpeed;
            document.body.classList.add('matrix-boost');

            setTimeout(() => {
                this.currentSpeed = this.normalSpeed;
                this.isBoostActive = false;
                document.body.classList.remove('matrix-boost');
            }, this.boostDuration);
        }
    }

    draw() {
        // Semi-transparent black background for trail effect
        this.ctx.fillStyle = `rgba(0, 0, 0, ${this.isBoostActive ? 0.1 : 0.05})`;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Matrix rain effect
        this.drops.forEach((drop, i) => {
            const char = this.characters[Math.floor(Math.random() * this.characters.length)];
            const x = i * this.fontSize;
            const y = drop * this.fontSize;

            // Brighter green during boost
            const brightness = Math.random() * 0.5 + 0.5;
            const green = this.isBoostActive ? 255 : 200;
            this.ctx.fillStyle = `rgba(0, ${green}, 0, ${brightness})`;
            this.ctx.fillText(char, x, y);

            // Update drop position
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            } else {
                this.drops[i] += this.currentSpeed;
            }
        });
    }

    animate() {
        if (!this.isAnimating) return;
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize singleton instance
document.addEventListener('DOMContentLoaded', () => {
    new MatrixAnimation();
});
