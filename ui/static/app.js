document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatCanvas = document.getElementById('chat-canvas');
    const welcomeView = document.getElementById('welcome-view');
    const card1 = document.getElementById('card-1');
    const card2 = document.getElementById('card-2');
    const card3 = document.getElementById('card-3');

    let currentState = 'WELCOME';

    function setState(state) {
        currentState = state;
        if (state !== 'WELCOME' && welcomeView) {
            welcomeView.style.display = 'none';
        }
        if (state === 'LOADING') {
            appendLoadingSkeleton();
        } else {
            removeLoadingSkeleton();
        }
        scrollToBottom();
    }

    function scrollToBottom() {
        if (chatCanvas) {
            chatCanvas.scrollTop = chatCanvas.scrollHeight;
        }
    }

    function appendUserBubble(text) {
        const bubble = document.createElement('div');
        bubble.className = 'flex justify-end w-full mb-4';
        bubble.innerHTML = `
            <div class="bg-primary-container text-on-primary p-4 rounded-xl rounded-tr-none max-w-[80%] shadow-sm">
                <p class="text-body-md font-body-md">${escapeHtml(text)}</p>
            </div>
        `;
        chatCanvas.appendChild(bubble);
        scrollToBottom();
    }

    function appendLoadingSkeleton() {
        const skeleton = document.createElement('div');
        skeleton.id = 'loading-skeleton';
        skeleton.className = 'flex justify-start w-full mb-4';
        skeleton.innerHTML = `
            <div class="flex gap-3 max-w-[85%]">
                <div class="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center shrink-0 mt-1">
                    <span class="material-symbols-outlined text-primary text-sm">robot_2</span>
                </div>
                <div class="bg-surface-container-low border-l-4 border-primary p-5 rounded-xl rounded-tl-none shadow-sm flex gap-1 items-center h-12">
                    <div class="w-2 h-2 rounded-full bg-primary animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 rounded-full bg-primary animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 rounded-full bg-primary animate-bounce" style="animation-delay: 300ms"></div>
                </div>
            </div>
        `;
        chatCanvas.appendChild(skeleton);
        scrollToBottom();
    }

    function removeLoadingSkeleton() {
        const skeleton = document.getElementById('loading-skeleton');
        if (skeleton) {
            skeleton.remove();
        }
    }

    function appendAssistantBubble(answer, sourceUrl, lastUpdated) {
        const bubble = document.createElement('div');
        bubble.className = 'flex justify-start w-full mb-4';
        bubble.innerHTML = `
            <div class="flex gap-3 max-w-[85%] w-full">
                <div class="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center shrink-0 mt-1">
                    <span class="material-symbols-outlined text-primary text-sm">robot_2</span>
                </div>
                <div class="bg-surface-container-low border-l-4 border-primary p-5 rounded-xl rounded-tl-none shadow-sm flex flex-col gap-3 w-full">
                    <p class="text-body-md font-body-md text-on-surface">
                        ${escapeHtml(answer)}
                    </p>
                    ${sourceUrl ? `
                    <div class="mt-2 pt-3 border-t border-surface-variant flex flex-wrap items-center justify-between gap-2">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-outline text-sm">find_in_page</span>
                            <span class="text-caption-sm font-caption-sm text-on-surface-variant">Source Link:</span>
                            <span class="text-caption-sm font-caption-sm text-on-surface">${escapeHtml(sourceUrl)}</span>
                        </div>
                        <a href="${sourceUrl}" target="_blank" class="inline-flex items-center gap-1 px-3 py-1.5 border border-surface-variant rounded-full text-caption-sm font-label-md text-primary hover:bg-primary/5 transition-colors">
                            View official source <span class="material-symbols-outlined text-xs">open_in_new</span>
                        </a>
                    </div>
                    ` : ''}
                    <div class="text-caption-sm font-caption-sm text-on-surface-variant mt-1">
                        Last updated: ${lastUpdated}
                    </div>
                </div>
            </div>
        `;
        chatCanvas.appendChild(bubble);
        scrollToBottom();
    }

    function appendRefusalBubble(message) {
        const bubble = document.createElement('div');
        bubble.className = 'flex justify-start w-full mb-4';
        bubble.innerHTML = `
            <div class="flex gap-3 max-w-[85%] w-full">
                <div class="w-8 h-8 rounded-full bg-tertiary-fixed flex items-center justify-center shrink-0 mt-1 text-on-tertiary-fixed">
                    <span class="material-symbols-outlined text-sm">warning</span>
                </div>
                <div class="bg-tertiary-fixed border-l-4 border-error p-5 rounded-xl rounded-tl-none shadow-sm flex flex-col gap-3 w-full">
                    <p class="text-body-md font-body-md text-on-tertiary-fixed-variant">
                        ${escapeHtml(message).replace(/\\n/g, '<br>')}
                    </p>
                    <div class="mt-2 pt-3 border-t border-surface-variant">
                        <a href="https://www.amfiindia.com/" target="_blank" class="text-caption-sm font-label-md text-primary underline">Visit AMFI India for details</a>
                    </div>
                    <div class="text-caption-sm font-caption-sm text-on-surface-variant mt-1 italic">
                        Facts-only. No investment advice.
                    </div>
                </div>
            </div>
        `;
        chatCanvas.appendChild(bubble);
        scrollToBottom();
    }

    function appendErrorBubble() {
        const bubble = document.createElement('div');
        bubble.className = 'flex justify-start w-full mb-4';
        bubble.innerHTML = `
            <div class="flex gap-3 max-w-[85%] w-full">
                <div class="w-8 h-8 rounded-full bg-error-container flex items-center justify-center shrink-0 mt-1 text-on-error-container">
                    <span class="material-symbols-outlined text-sm">error</span>
                </div>
                <div class="bg-error-container border-l-4 border-error p-5 rounded-xl rounded-tl-none shadow-sm w-full">
                    <p class="text-body-md font-body-md text-on-error-container">
                        Something went wrong. Please try again.
                    </p>
                </div>
            </div>
        `;
        chatCanvas.appendChild(bubble);
        scrollToBottom();
    }

    function escapeHtml(unsafe) {
        return (unsafe || '').toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async function sendMessage(query) {
        if (!query.trim()) return;

        setState('LOADING');
        appendUserBubble(query);
        chatInput.value = '';

        try {
            const API_BASE = 'https://mutualfund-faq-assistant-production.up.railway.app';
            const res = await fetch(`${API_BASE}/api/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query.trim() })
            });

            const data = await res.json();

            if (data.type === 'factual' || data.answer) {
                let answerStr = data.answer || "";

                // If there's an embedded source line, strip it
                if (answerStr && answerStr.includes('Source:')) {
                    answerStr = answerStr.split('Source:')[0].trim();
                }

                appendAssistantBubble(answerStr, data.source_url, data.last_updated);
                setState('ANSWER');
            } else if (data.type === 'advisory' || data.message) {
                appendRefusalBubble(data.message);
                setState('REFUSAL');
            } else {
                appendErrorBubble();
                setState('ERROR');
            }
        } catch (e) {
            console.error(e);
            appendErrorBubble();
            setState('ERROR');
        }
    }

    const handleSend = () => {
        sendMessage(chatInput.value);
    };

    if (sendBtn) sendBtn.addEventListener('click', handleSend);

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });
    }

    // Connect cards
    const attachCard = (cardElement) => {
        if (cardElement) {
            cardElement.addEventListener('click', () => {
                const questionText = cardElement.querySelector('span:nth-child(2)').innerText;
                sendMessage(questionText);
            });
        }
    };

    attachCard(card1);
    attachCard(card2);
    attachCard(card3);
});
