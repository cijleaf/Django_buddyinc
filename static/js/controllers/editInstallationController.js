var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('editInstallationController', function($scope, $rootScope, $uibModalInstance, currentUser, installation, API, utils) {
    //Set Object to equal Account
    $scope.installation = angular.copy(installation);

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.submitted = false;
    $scope.editInstallation = function() {
        $scope.submitted = true;
        API.editInstallation({
            id: $scope.installation.id,
            name: $scope.installation.name,
            address: $scope.installation.address,
            zip_code: $scope.installation.zip_code,
            state: $scope.installation.state,
            city: $scope.installation.city,
            community_code: $scope.installation.community_code,
        }).$promise.then(function() {
            $uibModalInstance.close($scope.installation);
        }).catch(utils.handleError);
    };
});