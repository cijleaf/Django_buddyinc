//Header
// used throughout
angular.module('mySunBuddy.common')
.directive('header', function(){
	return {
		restrict: 'AE',
		templateUrl: 'static/templates/Header.html'
	};
});
