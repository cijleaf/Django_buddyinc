var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('editAccountController', function($scope, $rootScope, $uibModalInstance, currentUser, profile, API, utils) {
    //Set Object to equal Account
    $scope.profile = angular.copy(profile);

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.submitted = false;
    $scope.editAccount = function() {
        if (!$scope.editAccountForm.$valid || !$scope.profile.state) {
            $scope.submitted = true;
            return
        }
        API.editAccount({
            name: $scope.profile.name,
            email: $scope.profile.email,
            phone: $scope.profile.phone,
            address: $scope.profile.address,
            zip_code: $scope.profile.zip_code,
            state: $scope.profile.state,
            city: $scope.profile.city
        }).$promise.then(function() {
            $uibModalInstance.close($scope.profile);
        }).catch(utils.handleError);
    };
});