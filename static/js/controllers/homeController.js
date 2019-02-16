//Home Controller
angular.module('mySunBuddy.public.home')
.controller('homeController',function($scope,$rootScope,$document,$routeParams, $uibModal){
	//Modal
	$scope.showSignInModal = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Sign_In.html',
            controller: 'signInController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function () {
        }, function () {});
    };
	$scope.role = '';
	//Scroll
	$scope.scrollTo = function(elem){
		$document.scrollToElement(angular.element(document.getElementById(elem)),0,500);	
	};

	if($routeParams.section){
		$scope.scrollTo($routeParams.section);
	}
});