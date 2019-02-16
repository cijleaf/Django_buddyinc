var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('certifyOwnershipController', function($scope, $rootScope, $uibModalInstance, currentUser, API, utils, Alert) {
    // $scope.profile = angular.copy(profile);

    $scope.cert_status = currentUser.profile.certification_status;

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.beneficial_owners = [];

    this.$onInit = function () {
        API.getBeneficialOwners().$promise.then(function(beneficial_owners) {
            $scope.beneficial_owners = beneficial_owners;
        }).catch(utils.handleError);
    };

    $scope.certifyOwnership = function () {
        API.certifyOwnership().$promise.then(function(r) {
            if(r.status === 'certified'){
                currentUser.profile.certification_status = 'certified';
                $scope.cert_status = 'certified';

                Alert.showSuccess('Certified successfully !');
            }else{
                Alert.showError('Certified Failed !');
            }
        }).catch(utils.handleError);
    }
});
