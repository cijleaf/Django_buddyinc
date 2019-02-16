var appControllers = angular.module('mySunBuddy.dashboard.common');

appControllers.controller('rejectSaleModalController', function($scope, $rootScope, $uibModalInstance, match, API, utils) {

    $scope.match = match;

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.rejectSale = function () {
        $scope.match.rejected = true;
        API.denyDeal({
            id: $scope.match.id
        }).$promise.then(function() {
            $uibModalInstance.close($scope.profile);
        }).catch(utils.handleError);
    };
});