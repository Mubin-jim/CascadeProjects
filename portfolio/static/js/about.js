// Typing animation for the header
const typeWriter = (element, text, speed = 100) => {
    let i = 0;
    element.innerHTML = '';
    const type = () => {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        } else {
            setTimeout(() => {
                element.classList.add('glow-strong');
                setTimeout(() => element.classList.remove('glow-strong'), 500);
            }, 200);
        }
    };
    type();
};

// Matrix rain effect
class MatrixRain {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.resizeCanvas();
        this.characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
        this.fontSize = 14;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = Array(this.columns).fill(1);
        
        window.addEventListener('resize', () => this.resizeCanvas());
        this.animate();
    }

    resizeCanvas() {
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = Array(this.columns).fill(1);
    }

    animate() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#0F0';
        this.ctx.font = this.fontSize + 'px monospace';
        
        for (let i = 0; i < this.drops.length; i++) {
            const char = this.characters[Math.floor(Math.random() * this.characters.length)];
            this.ctx.fillText(char, i * this.fontSize, this.drops[i] * this.fontSize);
            
            if (this.drops[i] * this.fontSize > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            this.drops[i]++;
        }
        requestAnimationFrame(() => this.animate());
    }
}

// Skill bar animation
const animateSkillBars = () => {
    const skillBars = document.querySelectorAll('.skill-progress');
    skillBars.forEach(bar => {
        const targetWidth = bar.parentElement.parentElement.dataset.skill;
        bar.style.width = '0%';
        setTimeout(() => {
            const width = bar.parentElement.previousElementSibling.querySelector('.skill-level').textContent;
            bar.style.width = width;
        }, 100);
    });
};

// Timeline animation
const animateTimeline = () => {
    const timelineItems = document.querySelectorAll('.timeline-item');
    timelineItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, 200 + (index * 200));
    });
};

// Profile card hover effect
const initializeProfileCard = () => {
    const card = document.querySelector('.profile-card');
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const angleX = (y - centerY) / 20;
        const angleY = (centerX - x) / 20;
        
        card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale(1.02)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
    });
};

// Floating tech tags
const animateTechTags = () => {
    const tags = document.querySelectorAll('.tech-tag');
    tags.forEach(tag => {
        tag.addEventListener('mouseover', () => {
            tag.style.transform = `translateY(-5px) rotate(${Math.random() * 10 - 5}deg)`;
        });
        
        tag.addEventListener('mouseout', () => {
            tag.style.transform = 'translateY(0) rotate(0)';
        });
    });
};

// Initialize all animations
document.addEventListener('DOMContentLoaded', () => {
    // Initialize matrix rain
    const canvas = document.querySelector('.matrix-rain');
    if (canvas) {
        new MatrixRain(canvas);
    }

    // Animate header text
    const header = document.querySelector('.about-header h1');
    if (header) {
        typeWriter(header, 'About Me');
    }

    // Force skill bars to be visible
    const skillsSection = document.querySelector('.skills-section');
    if (skillsSection) {
        skillsSection.style.display = 'block';
        skillsSection.style.opacity = '1';
        skillsSection.style.transform = 'none';
        
        // Initialize skill bars
        const skillBars = document.querySelectorAll('.skill-progress');
        skillBars.forEach(bar => {
            const width = bar.parentElement.previousElementSibling.querySelector('.skill-level').textContent;
            setTimeout(() => {
                bar.style.width = width;
            }, 500);
        });
    }

    // Initialize other animations
    initializeProfileCard();
    animateTimeline();
    animateTechTags();

    // Remove any stuck highlights
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        if (!link.classList.contains('active')) {
            link.style.transform = 'none';
            link.style.backgroundColor = 'transparent';
        }
    });
});

// Add scroll animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            if (entry.target.classList.contains('skills-section')) {
                animateSkillBars();
            }
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.skills-section, .experience-section').forEach(section => {
    observer.observe(section);
});
