//used in buyer and seller partials
angular.module('mySunBuddy.dashboard.common')
.directive('historical', function(){
	return {
		restrict: 'AE',
		templateUrl: 'static/templates/Historical.html'
	};
});