var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('setupSellerFundingController', function($scope, $rootScope, $uibModalInstance, currentUser, profile, API, utils) {
    $scope.profile = angular.copy(profile);
    $scope.businessClassifications = [];
    $scope.businessTypes = [
        {
            id: 'corporation',
            name: 'Corporation'
        },
        {
            id: 'llc',
            name: 'LLC'
        },
        {
            id: 'partnership',
            name: 'Partnership'
        },
    ];

    this.$onInit = function () {
        API.getBusinessClassifications().$promise.then(function(businessClassifications) {
            $scope.businessClassifications = businessClassifications;
        }).catch(utils.handleError);
    };

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.submitted = false;
    $scope.type = 'individual';

    $scope.setIndividual = function () {
        $scope.type = 'individual';
    };

    $scope.setBusiness = function () {
        $scope.type = 'business';
    };

    $scope.setupSellerFunding = function () {
        if (!$scope.setupSellerFundingForm.$valid || !$scope.profile.state) {
            $scope.submitted = true;
            return;
        }

        API.setupSellerFunding($scope.profile).$promise.then(function() {
            $uibModalInstance.close($scope.profile);
        }).catch(utils.handleError);
    };
});
