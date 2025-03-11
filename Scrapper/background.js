chrome.action.onClicked.addListener((tab) => {
  // Execute content script to gather links and handle clipboard
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: copyAllLinks
  });
});

// This function runs in the context of the web page
function copyAllLinks() {
  // Gather all links
  const links = document.querySelectorAll('a');
  let urls = [];
  
  links.forEach(link => {
    const href = link.href;
    if (href && !href.startsWith('javascript:')) {
      urls.push(href);
    }
  });
  
  const linksText = urls.join('\n');
  const linkCount = urls.length;
  
  // Copy to clipboard using the Clipboard API
  navigator.clipboard.writeText(linksText)
    .then(() => {
      // Show notification
      showNotification(linkCount);
    })
    .catch(err => {
      console.error('Failed to copy links: ', err);
      showNotification(0, true);
    });
}

function showNotification(linkCount, isError = false) {
  // Create notification element
  const notification = document.createElement('div');
  
  if (!isError) {
    notification.textContent = `\${linkCount} links copied to clipboard`;
    notification.style.backgroundColor = '#4285f4';
  } else {
    notification.textContent = 'Failed to copy links';
    notification.style.backgroundColor = '#ea4335';
  }
  
  // Style the notification
  notification.style.position = 'fixed';
  notification.style.top = '10px';
  notification.style.left = '50%';
  notification.style.transform = 'translateX(-50%)';
  notification.style.color = 'white';
  notification.style.padding = '10px 20px';
  notification.style.borderRadius = '4px';
  notification.style.zIndex = '999999';
  notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  notification.style.fontFamily = 'Arial, sans-serif';
  
  // Add to the page
  document.body.appendChild(notification);
  
  // Remove after a delay
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.5s';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 500);
  }, 2000);
}