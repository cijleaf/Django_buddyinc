var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('emailCustomersController', function($scope, $rootScope, $uibModalInstance, currentUser, installation, API, utils) {
    //Set Object to equal Account
    $scope.installation = angular.copy(installation);

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.submitted = false;
    $scope.sendEmail = function() {
        $scope.submitted = true;
        API.emailInstallationCustomers({
            id: $scope.installation.id,
            text: $scope.text,
        }).$promise.then(function() {
            $uibModalInstance.close($scope.installation);
        }).catch(utils.handleError);
    };
});