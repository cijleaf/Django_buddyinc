var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('communityCodeController', function($scope, $rootScope, $uibModalInstance, currentUser, profile, API, utils) {
    //Set Object to equal Account
    $scope.profile = angular.copy(profile);
    $scope.community_code = "";

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.remove = false;

    $scope.submitted = false;
    $scope.saveCode = function() {
        $scope.submitted = true;
        API.saveCommunityCode({
            community_code: $scope.community_code,
        }).$promise.then(function() {
            $uibModalInstance.close($scope.profile);
        }).catch(utils.handleError);
    };
});