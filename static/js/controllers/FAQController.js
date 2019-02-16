(function() {
  'use strict'
  
  angular
    .module('mySunBuddy.controllers')
    .controller('FAQController', FAQController);
  
  function FAQController() {
    var $ctrl = this;
    
    // Store the email in the controller rather than hardcoding it several times in the FAQ page
    $ctrl.mailtoEmail = 'info@mysunbuddy.com';
    
    $ctrl.termsOfUseLink = 'static/pdf/MySunBuddyWebsiteTermsofUse.pdf';
  }
})()
