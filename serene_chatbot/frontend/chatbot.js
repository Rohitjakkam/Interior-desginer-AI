/**
 * Serene Design Studio Chatbot Widget
 * A modern, embeddable chatbot for interior design services
 */

class SereneChatbot {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:8001',
            position: config.position || 'left', // 'left' or 'right'
            primaryColor: config.primaryColor || '#C9A961',
            companyName: config.companyName || 'Serene Design Studio',
            welcomeMessage: config.welcomeMessage || 'Need help with interior design? Chat with us!',
            showWelcomeTooltip: config.showWelcomeTooltip !== false,
            ...config
        };

        this.sessionId = this.getSessionId();
        this.isOpen = false;
        this.isLoading = false;
        this.messages = [];

        this.init();
    }

    getSessionId() {
        let sessionId = localStorage.getItem('serene_chat_session');
        if (!sessionId) {
            sessionId = 'sess_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
            localStorage.setItem('serene_chat_session', sessionId);
        }
        return sessionId;
    }

    init() {
        this.createWidget();
        this.attachEventListeners();

        // Show welcome tooltip after delay
        if (this.config.showWelcomeTooltip) {
            setTimeout(() => this.showWelcomeTooltip(), 3000);
        }
    }

    createWidget() {
        // Create main container
        const widget = document.createElement('div');
        widget.className = 'serene-chatbot-widget';
        widget.innerHTML = this.getWidgetHTML();
        document.body.appendChild(widget);

        // Cache DOM elements
        this.widget = widget;
        this.toggleBtn = widget.querySelector('.serene-chat-toggle');
        this.chatWindow = widget.querySelector('.serene-chat-window');
        this.messagesContainer = widget.querySelector('.serene-chat-messages');
        this.inputField = widget.querySelector('.serene-chat-input');
        this.sendBtn = widget.querySelector('.serene-chat-send');
        this.closeBtn = widget.querySelector('.serene-chat-close');
    }

    getWidgetHTML() {
        return `
            <!-- Chat Toggle Button -->
            <button class="serene-chat-toggle" aria-label="Open chat">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/>
                    <path d="M7 9h10v2H7zm0-3h10v2H7zm0 6h7v2H7z"/>
                </svg>
            </button>

            <!-- Chat Window -->
            <div class="serene-chat-window">
                <!-- Header -->
                <div class="serene-chat-header">
                    <div class="serene-chat-header-logo">SD</div>
                    <div class="serene-chat-header-info">
                        <div class="serene-chat-header-title">${this.config.companyName}</div>
                        <div class="serene-chat-header-subtitle">Interior Design Expert</div>
                    </div>
                    <button class="serene-chat-close" aria-label="Close chat">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>

                <!-- Messages -->
                <div class="serene-chat-messages"></div>

                <!-- Input Area -->
                <div class="serene-chat-input-area">
                    <input type="text" class="serene-chat-input" placeholder="Type your message..." maxlength="500">
                    <button class="serene-chat-send" aria-label="Send message">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Toggle button
        this.toggleBtn.addEventListener('click', () => this.toggle());

        // Close button
        this.closeBtn.addEventListener('click', () => this.close());

        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Input field - Enter key
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Disable send when empty
        this.inputField.addEventListener('input', () => {
            this.sendBtn.disabled = !this.inputField.value.trim();
        });

        // Initialize send button state
        this.sendBtn.disabled = true;
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    async open() {
        this.isOpen = true;
        this.chatWindow.classList.add('active');
        this.toggleBtn.classList.add('active');
        this.hideWelcomeTooltip();

        // Load greeting if first open
        if (this.messages.length === 0) {
            await this.loadGreeting();
        }

        // Focus input
        setTimeout(() => this.inputField.focus(), 300);
    }

    close() {
        this.isOpen = false;
        this.chatWindow.classList.remove('active');
        this.toggleBtn.classList.remove('active');
    }

    async loadGreeting() {
        try {
            const response = await fetch(`${this.config.apiUrl}/greeting?session_id=${this.sessionId}`);
            const data = await response.json();

            this.sessionId = data.session_id || this.sessionId;
            this.addBotMessage(data.response, data.quick_replies);
        } catch (error) {
            console.error('Failed to load greeting:', error);
            this.addBotMessage(
                "Hello! Welcome to Serene Design Studio. How can I help you with your interior design needs today?",
                ["Get Quote", "Our Services", "FAQs"]
            );
        }
    }

    async sendMessage(text = null) {
        const message = text || this.inputField.value.trim();
        if (!message || this.isLoading) return;

        // Clear input
        this.inputField.value = '';
        this.sendBtn.disabled = true;

        // Add user message
        this.addUserMessage(message);

        // Show typing indicator
        this.showTyping();

        try {
            const response = await fetch(`${this.config.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message
                })
            });

            const data = await response.json();

            this.hideTyping();
            this.sessionId = data.session_id || this.sessionId;

            // Check if we should show lead form
            if (data.action === 'collect_lead') {
                this.addBotMessage(data.response);
                this.showLeadForm();
            } else {
                this.addBotMessage(data.response, data.quick_replies);
            }

        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            this.addBotMessage(
                "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
                ["Try Again"]
            );
        }
    }

    addUserMessage(text) {
        const messageEl = document.createElement('div');
        messageEl.className = 'serene-message serene-message-user';
        messageEl.textContent = text;
        this.messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
        this.messages.push({ role: 'user', content: text });
    }

    addBotMessage(text, quickReplies = []) {
        const messageEl = document.createElement('div');
        messageEl.className = 'serene-message serene-message-bot';
        messageEl.innerHTML = this.formatMessage(text);
        this.messagesContainer.appendChild(messageEl);

        // Add quick replies if any
        if (quickReplies && quickReplies.length > 0) {
            const repliesEl = document.createElement('div');
            repliesEl.className = 'serene-quick-replies';
            quickReplies.forEach(reply => {
                const btn = document.createElement('button');
                btn.className = 'serene-quick-reply';
                btn.textContent = reply;
                btn.addEventListener('click', () => {
                    repliesEl.remove();
                    this.sendMessage(reply);
                });
                repliesEl.appendChild(btn);
            });
            this.messagesContainer.appendChild(repliesEl);
        }

        this.scrollToBottom();
        this.messages.push({ role: 'bot', content: text });
    }

    formatMessage(text) {
        // Convert markdown-style formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*)$/, '<p>$1</p>');
    }

    showTyping() {
        this.isLoading = true;
        const typingEl = document.createElement('div');
        typingEl.className = 'serene-typing';
        typingEl.id = 'serene-typing-indicator';
        typingEl.innerHTML = `
            <div class="serene-typing-dot"></div>
            <div class="serene-typing-dot"></div>
            <div class="serene-typing-dot"></div>
        `;
        this.messagesContainer.appendChild(typingEl);
        this.scrollToBottom();
    }

    hideTyping() {
        this.isLoading = false;
        const typingEl = document.getElementById('serene-typing-indicator');
        if (typingEl) typingEl.remove();
    }

    showLeadForm() {
        const formEl = document.createElement('div');
        formEl.className = 'serene-lead-form';
        formEl.innerHTML = `
            <h4>Get Your Free Estimate</h4>
            <div class="serene-form-group">
                <label>Name *</label>
                <input type="text" id="serene-lead-name" placeholder="Enter your name" required>
            </div>
            <div class="serene-form-group">
                <label>Mobile Number *</label>
                <input type="tel" id="serene-lead-mobile" placeholder="10-digit mobile number" pattern="[0-9]{10}" required>
            </div>
            <div class="serene-form-group">
                <label>Location *</label>
                <input type="text" id="serene-lead-location" placeholder="Your property location">
            </div>
            <div class="serene-form-group">
                <label>Property Type *</label>
                <select id="serene-lead-house-type">
                    <option value="">Select property type</option>
                    <option value="1RK">1RK</option>
                    <option value="1BHK">1BHK</option>
                    <option value="2BHK">2BHK</option>
                    <option value="3BHK">3BHK</option>
                    <option value="4BHK">4BHK</option>
                    <option value="Villa">Villa</option>
                    <option value="Penthouse">Penthouse</option>
                    <option value="Office">Office</option>
                    <option value="Shop">Shop</option>
                </select>
            </div>
            <div class="serene-form-group">
                <label>Budget Range *</label>
                <select id="serene-lead-budget">
                    <option value="">Select budget range</option>
                    <option value="Under 5 Lakhs">Under 5 Lakhs</option>
                    <option value="5-10 Lakhs">5-10 Lakhs</option>
                    <option value="10-15 Lakhs">10-15 Lakhs</option>
                    <option value="15-25 Lakhs">15-25 Lakhs</option>
                    <option value="25-50 Lakhs">25-50 Lakhs</option>
                    <option value="50 Lakhs+">50 Lakhs+</option>
                </select>
            </div>
            <button class="serene-form-submit" id="serene-lead-submit">Get Free Estimate</button>
        `;
        this.messagesContainer.appendChild(formEl);
        this.scrollToBottom();

        // Attach form submission handler
        document.getElementById('serene-lead-submit').addEventListener('click', () => this.submitLeadForm(formEl));
    }

    async submitLeadForm(formEl) {
        const name = document.getElementById('serene-lead-name').value.trim();
        const mobile = document.getElementById('serene-lead-mobile').value.trim();
        const location = document.getElementById('serene-lead-location').value.trim();
        const houseType = document.getElementById('serene-lead-house-type').value;
        const budget = document.getElementById('serene-lead-budget').value;

        // Validation
        if (!name || !mobile || !location || !houseType || !budget) {
            alert('Please fill in all fields');
            return;
        }

        if (!/^\d{10}$/.test(mobile)) {
            alert('Please enter a valid 10-digit mobile number');
            return;
        }

        const submitBtn = document.getElementById('serene-lead-submit');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            const response = await fetch(`${this.config.apiUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name,
                    mobile,
                    location,
                    house_type: houseType,
                    budget_range: budget,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                formEl.remove();
                this.addBotMessage(
                    "Thank you, " + name + "! Your request has been submitted successfully. Our design expert will contact you shortly to discuss your project. We look forward to helping you create your dream space!",
                    ["Explore Our Work", "Ask Another Question"]
                );
            } else {
                throw new Error(data.message || 'Submission failed');
            }

        } catch (error) {
            console.error('Registration error:', error);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Get Free Estimate';
            this.addBotMessage(
                "I apologize, but there was an issue submitting your request. Please try again or contact us directly.",
                ["Try Again"]
            );
        }
    }

    showWelcomeTooltip() {
        if (this.isOpen) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'serene-welcome-tooltip';
        tooltip.id = 'serene-welcome-tooltip';
        tooltip.innerHTML = `
            <button class="serene-welcome-tooltip-close">&times;</button>
            <p>${this.config.welcomeMessage}</p>
        `;
        this.widget.appendChild(tooltip);

        tooltip.querySelector('.serene-welcome-tooltip-close').addEventListener('click', () => {
            this.hideWelcomeTooltip();
        });

        // Auto-hide after 10 seconds
        setTimeout(() => this.hideWelcomeTooltip(), 10000);
    }

    hideWelcomeTooltip() {
        const tooltip = document.getElementById('serene-welcome-tooltip');
        if (tooltip) tooltip.remove();
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
}

// Auto-initialize if config is present
if (typeof window.SERENE_CHATBOT_CONFIG !== 'undefined') {
    window.sereneChatbot = new SereneChatbot(window.SERENE_CHATBOT_CONFIG);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SereneChatbot;
}
