var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('calculateCreditsController', function($scope, $rootScope, $uibModalInstance, currentUser, installation, API, utils) {
    //Set Object to equal Account
    $scope.installation = angular.copy(installation);

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.long;
    $scope.lat;
    $scope.system_capacity;
    $scope.module_type;
    $scope.address = $scope.installation.address +", "+ $scope.installation.city +", "+ $scope.installation.state +", "+ $scope.installation.zip_code;

    $scope.submitted = false;
    $scope.calculateCredits = function() {
        $scope.submitted = true;
        API.calculateCredits({
            id: $scope.installation.id,
            address: $scope.address,
            lat: $scope.lat,
            long: $scope.long,
            module_type: $scope.module_type,
            system_capacity: $scope.system_capacity,
        }).$promise.then(function() {
            $uibModalInstance.close($scope.installation);
        }).catch(utils.handleError);
    };
});