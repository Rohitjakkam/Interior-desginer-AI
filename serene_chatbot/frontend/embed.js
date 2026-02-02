/**
 * Serene Design Studio Chatbot - Single File Embed Script
 * Include this script on any website to add the chatbot widget
 *
 * Usage:
 * <script src="path/to/embed.js" data-api-url="http://your-server:8001"></script>
 */

(function() {
    'use strict';

    // Get configuration from script tag
    const currentScript = document.currentScript;
    const apiUrl = currentScript?.getAttribute('data-api-url') || 'http://localhost:8001';
    const position = currentScript?.getAttribute('data-position') || 'left';
    const primaryColor = currentScript?.getAttribute('data-color') || '#C9A961';

    // CSS Styles (embedded)
    const styles = `
        .serene-chatbot-widget * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .serene-chatbot-widget {
            position: fixed;
            bottom: 20px;
            ${position === 'right' ? 'right: 20px;' : 'left: 20px;'}
            z-index: 999999;
            font-size: 14px;
        }
        .serene-chat-toggle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, ${primaryColor}, ${adjustColor(primaryColor, -20)});
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .serene-chat-toggle:hover {
            transform: scale(1.1);
        }
        .serene-chat-toggle svg {
            width: 28px;
            height: 28px;
            fill: white;
        }
        .serene-chat-window {
            position: absolute;
            bottom: 75px;
            ${position === 'right' ? 'right: 0;' : 'left: 0;'}
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: none;
            flex-direction: column;
            overflow: hidden;
        }
        .serene-chat-window.active {
            display: flex;
            animation: slideUp 0.3s ease;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .serene-chat-header {
            background: linear-gradient(135deg, ${primaryColor}, ${adjustColor(primaryColor, -20)});
            color: white;
            padding: 18px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .serene-chat-header-logo {
            width: 45px;
            height: 45px;
            background: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: ${primaryColor};
            font-size: 16px;
        }
        .serene-chat-header-info { flex: 1; }
        .serene-chat-header-title { font-size: 16px; font-weight: 600; }
        .serene-chat-header-subtitle { font-size: 12px; opacity: 0.9; }
        .serene-chat-close {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 5px;
        }
        .serene-chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            background: #f5f5f5;
        }
        .serene-message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            line-height: 1.5;
        }
        .serene-message-bot {
            background: white;
            color: #2c2c2c;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .serene-message-user {
            background: linear-gradient(135deg, ${primaryColor}, ${adjustColor(primaryColor, -20)});
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .serene-typing {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            background: white;
            border-radius: 16px;
            align-self: flex-start;
        }
        .serene-typing-dot {
            width: 8px;
            height: 8px;
            background: ${primaryColor};
            border-radius: 50%;
            animation: bounce 1.4s infinite;
        }
        .serene-typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .serene-typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        .serene-quick-replies {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .serene-quick-reply {
            background: white;
            border: 1.5px solid ${primaryColor};
            color: ${primaryColor};
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        .serene-quick-reply:hover {
            background: ${primaryColor};
            color: white;
        }
        .serene-chat-input-area {
            padding: 15px 20px;
            background: white;
            border-top: 1px solid #f0f0f0;
            display: flex;
            gap: 10px;
        }
        .serene-chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1.5px solid #e0e0e0;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        .serene-chat-input:focus {
            border-color: ${primaryColor};
        }
        .serene-chat-send {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: linear-gradient(135deg, ${primaryColor}, ${adjustColor(primaryColor, -20)});
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .serene-chat-send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .serene-chat-send svg {
            width: 20px;
            height: 20px;
            fill: white;
        }
        .serene-lead-form {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
        }
        .serene-lead-form h4 {
            margin-bottom: 15px;
            color: #2c2c2c;
        }
        .serene-form-group {
            margin-bottom: 12px;
        }
        .serene-form-group label {
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        .serene-form-group input,
        .serene-form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1.5px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }
        .serene-form-submit {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, ${primaryColor}, ${adjustColor(primaryColor, -20)});
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
        }
        @media (max-width: 480px) {
            .serene-chat-window {
                width: calc(100vw - 40px);
                height: calc(100vh - 100px);
            }
        }
    `;

    // Helper function to adjust color brightness
    function adjustColor(color, amount) {
        const hex = color.replace('#', '');
        const r = Math.max(0, Math.min(255, parseInt(hex.substr(0, 2), 16) + amount));
        const g = Math.max(0, Math.min(255, parseInt(hex.substr(2, 2), 16) + amount));
        const b = Math.max(0, Math.min(255, parseInt(hex.substr(4, 2), 16) + amount));
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    // Inject styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // Chatbot Class
    class SereneChatbotEmbed {
        constructor() {
            this.sessionId = this.getSessionId();
            this.isOpen = false;
            this.isLoading = false;
            this.messages = [];
            this.init();
        }

        getSessionId() {
            let id = localStorage.getItem('serene_session');
            if (!id) {
                id = 'sess_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('serene_session', id);
            }
            return id;
        }

        init() {
            const widget = document.createElement('div');
            widget.className = 'serene-chatbot-widget';
            widget.innerHTML = `
                <button class="serene-chat-toggle">
                    <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/></svg>
                </button>
                <div class="serene-chat-window">
                    <div class="serene-chat-header">
                        <div class="serene-chat-header-logo">SD</div>
                        <div class="serene-chat-header-info">
                            <div class="serene-chat-header-title">Serene Design Studio</div>
                            <div class="serene-chat-header-subtitle">Interior Design Expert</div>
                        </div>
                        <button class="serene-chat-close">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                        </button>
                    </div>
                    <div class="serene-chat-messages"></div>
                    <div class="serene-chat-input-area">
                        <input type="text" class="serene-chat-input" placeholder="Type your message...">
                        <button class="serene-chat-send" disabled>
                            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(widget);

            this.widget = widget;
            this.toggle = widget.querySelector('.serene-chat-toggle');
            this.window = widget.querySelector('.serene-chat-window');
            this.messages_el = widget.querySelector('.serene-chat-messages');
            this.input = widget.querySelector('.serene-chat-input');
            this.send = widget.querySelector('.serene-chat-send');
            this.close = widget.querySelector('.serene-chat-close');

            this.toggle.onclick = () => this.toggleChat();
            this.close.onclick = () => this.closeChat();
            this.send.onclick = () => this.sendMessage();
            this.input.onkeypress = (e) => e.key === 'Enter' && this.sendMessage();
            this.input.oninput = () => this.send.disabled = !this.input.value.trim();
        }

        toggleChat() {
            this.isOpen ? this.closeChat() : this.openChat();
        }

        async openChat() {
            this.isOpen = true;
            this.window.classList.add('active');
            if (this.messages.length === 0) await this.loadGreeting();
            this.input.focus();
        }

        closeChat() {
            this.isOpen = false;
            this.window.classList.remove('active');
        }

        async loadGreeting() {
            try {
                const res = await fetch(`${apiUrl}/greeting?session_id=${this.sessionId}`);
                const data = await res.json();
                this.addBotMsg(data.response, data.quick_replies);
            } catch {
                this.addBotMsg("Hello! Welcome to Serene Design Studio. How can I help you?", ["Get Quote", "Our Services"]);
            }
        }

        async sendMessage(text = null) {
            const msg = text || this.input.value.trim();
            if (!msg || this.isLoading) return;
            this.input.value = '';
            this.send.disabled = true;
            this.addUserMsg(msg);
            this.showTyping();

            try {
                const res = await fetch(`${apiUrl}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: this.sessionId, message: msg })
                });
                const data = await res.json();
                this.hideTyping();
                if (data.action === 'collect_lead') {
                    this.addBotMsg(data.response);
                    this.showLeadForm();
                } else {
                    this.addBotMsg(data.response, data.quick_replies);
                }
            } catch {
                this.hideTyping();
                this.addBotMsg("Sorry, I'm having connection issues. Please try again.");
            }
        }

        addUserMsg(text) {
            const el = document.createElement('div');
            el.className = 'serene-message serene-message-user';
            el.textContent = text;
            this.messages_el.appendChild(el);
            this.scroll();
            this.messages.push({ role: 'user', content: text });
        }

        addBotMsg(text, replies = []) {
            const el = document.createElement('div');
            el.className = 'serene-message serene-message-bot';
            el.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
            this.messages_el.appendChild(el);
            if (replies.length) {
                const rpl = document.createElement('div');
                rpl.className = 'serene-quick-replies';
                replies.forEach(r => {
                    const btn = document.createElement('button');
                    btn.className = 'serene-quick-reply';
                    btn.textContent = r;
                    btn.onclick = () => { rpl.remove(); this.sendMessage(r); };
                    rpl.appendChild(btn);
                });
                this.messages_el.appendChild(rpl);
            }
            this.scroll();
        }

        showTyping() {
            this.isLoading = true;
            const el = document.createElement('div');
            el.className = 'serene-typing';
            el.id = 'typing';
            el.innerHTML = '<div class="serene-typing-dot"></div><div class="serene-typing-dot"></div><div class="serene-typing-dot"></div>';
            this.messages_el.appendChild(el);
            this.scroll();
        }

        hideTyping() {
            this.isLoading = false;
            document.getElementById('typing')?.remove();
        }

        showLeadForm() {
            const form = document.createElement('div');
            form.className = 'serene-lead-form';
            form.innerHTML = `
                <h4>Get Your Free Estimate</h4>
                <div class="serene-form-group"><label>Name</label><input id="ln" placeholder="Your name"></div>
                <div class="serene-form-group"><label>Mobile</label><input id="lm" placeholder="10-digit number"></div>
                <div class="serene-form-group"><label>Location</label><input id="ll" placeholder="Property location"></div>
                <div class="serene-form-group"><label>Property Type</label><select id="lh"><option value="">Select</option><option>1BHK</option><option>2BHK</option><option>3BHK</option><option>Villa</option><option>Office</option></select></div>
                <div class="serene-form-group"><label>Budget</label><select id="lb"><option value="">Select</option><option>Under 5L</option><option>5-10L</option><option>10-25L</option><option>25L+</option></select></div>
                <button class="serene-form-submit" id="ls">Submit</button>
            `;
            this.messages_el.appendChild(form);
            this.scroll();
            document.getElementById('ls').onclick = () => this.submitLead(form);
        }

        async submitLead(form) {
            const n = document.getElementById('ln').value.trim();
            const m = document.getElementById('lm').value.trim();
            const l = document.getElementById('ll').value.trim();
            const h = document.getElementById('lh').value;
            const b = document.getElementById('lb').value;
            if (!n || !m || !l || !h || !b) { alert('Please fill all fields'); return; }
            if (!/^\d{10}$/.test(m)) { alert('Enter valid 10-digit mobile'); return; }
            try {
                const res = await fetch(`${apiUrl}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: n, mobile: m, location: l, house_type: h, budget_range: b, session_id: this.sessionId })
                });
                const data = await res.json();
                if (data.success) {
                    form.remove();
                    this.addBotMsg(`Thank you ${n}! Our team will contact you shortly.`, ["Ask Question"]);
                }
            } catch { alert('Submission failed. Please try again.'); }
        }

        scroll() {
            setTimeout(() => this.messages_el.scrollTop = this.messages_el.scrollHeight, 100);
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new SereneChatbotEmbed());
    } else {
        new SereneChatbotEmbed();
    }
})();
