var appControllers = angular.module('mySunBuddy.dashboard.common');

appControllers.controller('signDealModalController', function($scope, $rootScope, $location, $uibModalInstance, match, API, utils) {

    $scope.match = match;
    $scope.signing = false;

    // TODO: make this dynamic
    $scope.contractUrl = '/static/pdf/nationalgrid_schedule_z.pdf';

    $scope.cancel = function() {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.signDeal = function() {
        $scope.signing = true;
        API.signDeal({
            id: $scope.match.id,
            initials: $scope.initials
        }).$promise.then(function() {
            $uibModalInstance.close($scope.profile);
            $location.path('/Seller_Account_Portal');
            location.reload();
        }).catch(utils.handleError).finally(function() {
            $scope.signing = false;
        })
    };

    $scope.previewContract = function() {
        $scope.signing = true;
        API.previewDeal({
            id: $scope.match.id,
            initials: $scope.initials
        }).$promise.finally(function() {
            $scope.signing = false;
        });
    }

});