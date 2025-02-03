// Google Consent implemntation
function updateConsent(consent) {
  gtag('consent', 'update', {
    'ad_storage': consent.marketing ? 'granted' : 'denied',
    'analytics_storage': consent.analytics ? 'granted' : 'denied'
  });
}

// Example: User accepts analytics but declines marketing
updateConsent({ analytics: true, marketing: false });
