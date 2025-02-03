// Google Consent implemntation
function updateConsent(consent) {
  gtag('consent', 'update', {
    'ad_storage': consent.marketing ? 'granted' : 'denied',
    'analytics_storage': consent.analytics ? 'granted' : 'denied'
  });
}

// Example: User accepts analytics but declines marketing
updateConsent({ analytics: true, marketing: false });

document.addEventListener('DOMContentLoaded', function() {
  const consentPopup = document.getElementById('consent-popup');
  const acceptButton = document.getElementById('accept');
  const rejectButton = document.getElementById('reject');

  if (!localStorage.getItem('consentGiven')) {
    consentPopup.style.display = 'block';
  }

  acceptButton.addEventListener('click', function() {
    updateConsent({ analytics: true, marketing: true });
    localStorage.setItem('consentGiven', 'true');
    consentPopup.style.display = 'none';
  });

  rejectButton.addEventListener('click', function() {
    updateConsent({ analytics: false, marketing: false });
    localStorage.setItem('consentGiven', 'true');
    consentPopup.style.display = 'none';
  });
});

