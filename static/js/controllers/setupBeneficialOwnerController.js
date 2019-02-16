var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('setupBeneficialOwnerController', function($scope, $rootScope, $uibModalInstance, currentUser, profile, API, utils) {
    $scope.profile = angular.copy(profile);

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.submitted = false;

    $scope.submitBeneficialOwner = function () {
        if (!$scope.setupBeneficialForm.$valid || !$scope.profile.state) {
            $scope.submitted = true;
            return;
        }

        API.setupBeneficialOwner($scope.profile).$promise.then(function(r) {
            currentUser.profile.certification_status = r.cert_status;

            $uibModalInstance.close($scope.profile);
        }).catch(utils.handleError);
    };
});
