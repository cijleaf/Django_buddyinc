//Notification
//used in buyer and seller partials
angular.module('mySunBuddy.dashboard.common')
.directive('notifications', function(){
	return {
		restrict: 'AE',
		templateUrl: 'static/templates/Notifications.html'
	};
});