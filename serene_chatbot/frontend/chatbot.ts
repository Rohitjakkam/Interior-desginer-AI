/**
 * Serene Design Studio Chatbot Widget
 * A modern, embeddable chatbot for interior design services
 */

interface ChatbotConfig {
    apiUrl: string;
    position: 'left' | 'right';
    primaryColor: string;
    companyName: string;
    welcomeMessage: string;
    showWelcomeTooltip: boolean;
}

interface ChatMessage {
    role: 'user' | 'bot';
    content: string;
    timestamp?: string;
}

interface ChatResponse {
    response: string;
    quick_replies: string[];
    action: 'none' | 'collect_lead' | 'show_form';
    session_id: string;
}

interface LeadData {
    name: string;
    mobile: string;
    location: string;
    house_type: string;
    budget_range: string;
    session_id: string;
}

interface LeadResponse {
    success: boolean;
    message: string;
    lead_id?: string;
}

class SereneChatbot {
    private config: ChatbotConfig;
    private sessionId: string;
    private isOpen: boolean = false;
    private isLoading: boolean = false;
    private messages: ChatMessage[] = [];

    // DOM Elements
    private widget!: HTMLDivElement;
    private toggleBtn!: HTMLButtonElement;
    private chatWindow!: HTMLDivElement;
    private messagesContainer!: HTMLDivElement;
    private inputField!: HTMLInputElement;
    private sendBtn!: HTMLButtonElement;
    private closeBtn!: HTMLButtonElement;

    constructor(config: Partial<ChatbotConfig> = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:8001',
            position: config.position || 'left',
            primaryColor: config.primaryColor || '#C9A961',
            companyName: config.companyName || 'Serene Design Studio',
            welcomeMessage: config.welcomeMessage || 'Need help with interior design? Chat with us!',
            showWelcomeTooltip: config.showWelcomeTooltip !== false,
        };

        this.sessionId = this.getSessionId();
        this.init();
    }

    private getSessionId(): string {
        let sessionId = localStorage.getItem('serene_chat_session');
        if (!sessionId) {
            sessionId = 'sess_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
            localStorage.setItem('serene_chat_session', sessionId);
        }
        return sessionId;
    }

    private init(): void {
        this.createWidget();
        this.attachEventListeners();

        if (this.config.showWelcomeTooltip) {
            setTimeout(() => this.showWelcomeTooltip(), 3000);
        }
    }

    private createWidget(): void {
        const widget = document.createElement('div');
        widget.className = 'serene-chatbot-widget';
        widget.innerHTML = this.getWidgetHTML();
        document.body.appendChild(widget);

        this.widget = widget;
        this.toggleBtn = widget.querySelector('.serene-chat-toggle') as HTMLButtonElement;
        this.chatWindow = widget.querySelector('.serene-chat-window') as HTMLDivElement;
        this.messagesContainer = widget.querySelector('.serene-chat-messages') as HTMLDivElement;
        this.inputField = widget.querySelector('.serene-chat-input') as HTMLInputElement;
        this.sendBtn = widget.querySelector('.serene-chat-send') as HTMLButtonElement;
        this.closeBtn = widget.querySelector('.serene-chat-close') as HTMLButtonElement;
    }

    private getWidgetHTML(): string {
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

    private attachEventListeners(): void {
        this.toggleBtn.addEventListener('click', () => this.toggle());
        this.closeBtn.addEventListener('click', () => this.close());
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        this.inputField.addEventListener('keypress', (e: KeyboardEvent) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.inputField.addEventListener('input', () => {
            this.sendBtn.disabled = !this.inputField.value.trim();
        });

        this.sendBtn.disabled = true;
    }

    public toggle(): void {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    public async open(): Promise<void> {
        this.isOpen = true;
        this.chatWindow.classList.add('active');
        this.toggleBtn.classList.add('active');
        this.hideWelcomeTooltip();

        if (this.messages.length === 0) {
            await this.loadGreeting();
        }

        setTimeout(() => this.inputField.focus(), 300);
    }

    public close(): void {
        this.isOpen = false;
        this.chatWindow.classList.remove('active');
        this.toggleBtn.classList.remove('active');
    }

    private async loadGreeting(): Promise<void> {
        try {
            const response = await fetch(`${this.config.apiUrl}/greeting?session_id=${this.sessionId}`);
            const data: ChatResponse = await response.json();

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

    public async sendMessage(text: string | null = null): Promise<void> {
        const message = text || this.inputField.value.trim();
        if (!message || this.isLoading) return;

        this.inputField.value = '';
        this.sendBtn.disabled = true;

        this.addUserMessage(message);
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

            const data: ChatResponse = await response.json();

            this.hideTyping();
            this.sessionId = data.session_id || this.sessionId;

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

    private addUserMessage(text: string): void {
        const messageEl = document.createElement('div');
        messageEl.className = 'serene-message serene-message-user';
        messageEl.textContent = text;
        this.messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
        this.messages.push({ role: 'user', content: text });
    }

    private addBotMessage(text: string, quickReplies: string[] = []): void {
        const messageEl = document.createElement('div');
        messageEl.className = 'serene-message serene-message-bot';
        messageEl.innerHTML = this.formatMessage(text);
        this.messagesContainer.appendChild(messageEl);

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

    private formatMessage(text: string): string {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*)$/, '<p>$1</p>');
    }

    private showTyping(): void {
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

    private hideTyping(): void {
        this.isLoading = false;
        const typingEl = document.getElementById('serene-typing-indicator');
        if (typingEl) typingEl.remove();
    }

    private showLeadForm(): void {
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

        const submitBtn = document.getElementById('serene-lead-submit') as HTMLButtonElement;
        submitBtn.addEventListener('click', () => this.submitLeadForm(formEl));
    }

    private async submitLeadForm(formEl: HTMLDivElement): Promise<void> {
        const name = (document.getElementById('serene-lead-name') as HTMLInputElement).value.trim();
        const mobile = (document.getElementById('serene-lead-mobile') as HTMLInputElement).value.trim();
        const location = (document.getElementById('serene-lead-location') as HTMLInputElement).value.trim();
        const houseType = (document.getElementById('serene-lead-house-type') as HTMLSelectElement).value;
        const budget = (document.getElementById('serene-lead-budget') as HTMLSelectElement).value;

        if (!name || !mobile || !location || !houseType || !budget) {
            alert('Please fill in all fields');
            return;
        }

        if (!/^\d{10}$/.test(mobile)) {
            alert('Please enter a valid 10-digit mobile number');
            return;
        }

        const submitBtn = document.getElementById('serene-lead-submit') as HTMLButtonElement;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            const leadData: LeadData = {
                name,
                mobile,
                location,
                house_type: houseType,
                budget_range: budget,
                session_id: this.sessionId
            };

            const response = await fetch(`${this.config.apiUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(leadData)
            });

            const data: LeadResponse = await response.json();

            if (data.success) {
                formEl.remove();
                this.addBotMessage(
                    `Thank you, ${name}! Your request has been submitted successfully. Our design expert will contact you shortly to discuss your project. We look forward to helping you create your dream space!`,
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

    private showWelcomeTooltip(): void {
        if (this.isOpen) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'serene-welcome-tooltip';
        tooltip.id = 'serene-welcome-tooltip';
        tooltip.innerHTML = `
            <button class="serene-welcome-tooltip-close">&times;</button>
            <p>${this.config.welcomeMessage}</p>
        `;
        this.widget.appendChild(tooltip);

        const closeBtn = tooltip.querySelector('.serene-welcome-tooltip-close') as HTMLButtonElement;
        closeBtn.addEventListener('click', () => {
            this.hideWelcomeTooltip();
        });

        setTimeout(() => this.hideWelcomeTooltip(), 10000);
    }

    private hideWelcomeTooltip(): void {
        const tooltip = document.getElementById('serene-welcome-tooltip');
        if (tooltip) tooltip.remove();
    }

    private scrollToBottom(): void {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
}

// Type declaration for global config
declare global {
    interface Window {
        SERENE_CHATBOT_CONFIG?: Partial<ChatbotConfig>;
        sereneChatbot?: SereneChatbot;
    }
}

// Auto-initialize if config is present
if (typeof window.SERENE_CHATBOT_CONFIG !== 'undefined') {
    window.sereneChatbot = new SereneChatbot(window.SERENE_CHATBOT_CONFIG);
}

export { SereneChatbot, ChatbotConfig, ChatMessage, ChatResponse, LeadData, LeadResponse };
