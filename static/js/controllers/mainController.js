//Main Controller
angular.module('mySunBuddy.common')
.controller('mainController', function($scope, $rootScope, $window){
	//Modal
	$rootScope.modal = {
		show: false,
		type: ''
	};

	//For viewing pdfs -- this should eventually be updated to use angular-pdf
    $scope.terms = "static/pdf/TermsOfService.pdf";
    $scope.privacy = "static/pdf/PrivacyPolicy.pdf";
    $scope.openPdf = function(pdfName) {
        $window.open(pdfName);
    };
});




