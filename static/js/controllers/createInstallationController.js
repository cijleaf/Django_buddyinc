var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('createInstallationController', function($scope, $rootScope, $uibModalInstance, currentUser, profile, API, utils) {
    //Set Object to equal Account
    $scope.profile = angular.copy(profile);

    $scope.installation = {};

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.submitted = false;
    $scope.createInstallation = function() {
        $scope.submitted = true;
        API.createInstallation({
            name: $scope.installation.name,
            address: $scope.installation.address,
            zip_code: $scope.installation.zip_code,
            state: $scope.installation.state,
            city: $scope.installation.city,
            community_code: $scope.installation.community_code,
        }).$promise.then(function() {
            $uibModalInstance.close($scope.profile);
        }).catch(utils.handleError);
    };
});