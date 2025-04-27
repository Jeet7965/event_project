// function toggleChat() {
//   const box = document.getElementById('chat-box');
//   box.classList.toggle('hidden');
// }

// function sendMessage() {
//   const input = document.getElementById('chat-input');
//   const message = input.value.trim();
//   if (!message) return;

//   addMessage('user', message);
//   input.value = '';

//   fetch('/chat/send/', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'X-CSRFToken': csrftoken
//     },
//     body: JSON.stringify({ message })
//   })
//   .then(res => res.json())
//   .then(data => {
//     addMessage('bot', data.reply);
//   });
// }

// function addMessage(sender, text) {
//   const chat = document.getElementById('chat-messages');
//   const div = document.createElement('div');
//   div.className = `p-2 rounded-lg max-w-[75%] ${
//     sender === 'user'
//       ? 'bg-blue-100 self-end text-right'
//       : 'bg-gray-200 self-start text-left'
//   }`;
//   div.innerText = text;
//   chat.appendChild(div);
//   chat.scrollTop = chat.scrollHeight;
// }


function toggleChat() {
  const chatBox = document.getElementById('chat-box');
  chatBox.classList.toggle('hidden');
}

function sendMessage() {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (message) {
    const messageContainer = document.getElementById('chat-messages');
    const userMessage = document.createElement('div');
    userMessage.className = 'self-end bg-blue-100 text-gray-900 px-3 py-2 rounded-lg max-w-xs';
    userMessage.textContent = message;
    messageContainer.appendChild(userMessage);
    input.value = '';
    messageContainer.scrollTop = messageContainer.scrollHeight;
    // Handle response here if needed
  }
}