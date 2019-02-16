//Sign In Controller
angular.module('mySunBuddy.public.signIn')
.controller('signInController',function($scope, $filter, $location, $uibModal, $uibModalInstance, API, currentUser, utils, ConfigURLs){
    $scope.result = '';	
    $scope.user = {
        login: '',
        password: ''	
    };
    $scope.recaptcha_sitekey = ConfigURLs.recaptcha_sitekey;

	$scope.showForgotPasswordModal = function() {
	    $uibModalInstance.dismiss('cancel');
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Forgot_Password.html',
            controller: 'forgotPasswordController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function () {
        }, function () {});
    };

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.signIn = function(){
        $scope.result = '';
        if(typeof $scope.user === 'undefined' || (!$scope.user.login || !$scope.user.password)){
            $scope.result = 'empty';
        } else {
            API.login($scope.user).$promise
            .then(function(profile){
                currentUser.update(profile);
                $uibModalInstance.close();
                if (currentUser.profile.role=='seller') {
                    $location.path("/Seller");
                } else if (currentUser.profile.role=='buyer') {
                    $location.path("/Buyer_Account_Portal");
                } else if (currentUser.profile.role=='community_solar') {
                    $location.path("/Community_Account_Portal");
                }
            }).catch(function(error){
                var errors= utils.parseError(error);
                $scope.result = 'error';
                if (error.status === 429 && error.statusText === 'TOO MANY REQUESTS') {
                  // Overwrite result as 'throttled' to display a more specific type of error message.
                  $scope.result = 'throttled';

                  // Splitting from message: 'Request was throttled. Expected available in 53 seconds.'
                  // in order to obtain the waitMessage as '53 seconds.'
                  var waitTime = error.data.detail.split(' in ')[1];
                  $scope.waitMessage = 'Too many login attempts. Try again in ' + waitTime;
                } else if (errors.length) {
                    if(errors[0] == 'User account is disabled.') {
                         $scope.result = 'disabled';
                    }
                }
            });
        }
    };
    $scope.getFocus = function(){
        $scope.result = '';
    };
});