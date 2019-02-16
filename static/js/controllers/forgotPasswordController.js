//Forgot Password controller
angular.module('mySunBuddy.public.signIn')
.controller('forgotPasswordController',function($scope,$rootScope,$location,$routeParams, $uibModalInstance, API, utils) {
	//Modal
    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

	$scope.role = '';
	$scope.result = '';
	$scope.user = {
		login: ''
    };

	$scope.resetPassword = function(){
		$scope.result = '';
		if(typeof $scope.user === 'undefined' || !$scope.user.login){
				$scope.result = 'Email is empty, please enter a valid address!';
		}else{
		    $uibModalInstance.close();
			API.resetPassword($scope.user).$promise
			.then(function(){
					$rootScope.modal.show = false;
				}).catch(utils.handleError);
		}
	};

});