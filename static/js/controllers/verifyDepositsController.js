var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('verifyDepositsController', function($scope, $rootScope, $uibModalInstance, currentUser, profile, API, utils) {
    $scope.profile = angular.copy(profile);
    $scope.submitted = false;
    $scope.form = {};

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.verifyDeposits = function () {
        if (!$scope.verifyDepositsForm.$valid || !$scope.profile.state) {
            $scope.submitted = true;
            return;
        }

        API.verifyDeposits($scope.form).$promise.then(function(response) {
            $scope.profile.funding_status = response.funding_status;
            $uibModalInstance.close($scope.profile);
        }).catch(utils.handleError);
    };
});
