var appControllers = angular.module('mySunBuddy.dashboard.common');
appControllers.controller('uploadVerificationDocumentController', function($scope, $rootScope, $uibModalInstance, currentUser, profile, API, utils, $http) {
    $scope.profile = angular.copy(profile);
    $scope.form = {};
    $scope.documentTypes = [
        {
            id: 'passport',
            name: 'Passport'
        },
        {
            id: 'license',
            name: 'License'
        },
        {
            id: 'idCard',
            name: 'Identification card'
        },
        {
            id: 'other',
            name: 'Other'
        },
    ];

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.submitted = false;

    $scope.uploadVerificationDocument = function () {
        if (!$scope.uploadVerificationDocumentForm.$valid || !$scope.profile.state) {
            $scope.submitted = true;
            return;
        }

        var formData = new FormData();
        formData.append('document_type', $scope.form.document_type);
        formData.append('file', document.getElementById('documentFile').files[0]);

        $http.post('/api/account/upload-verification-document', formData, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        }).success(function () {
            $uibModalInstance.close($scope.profile);
        }).error(function (error) {
            utils.handleError({ data: JSON.parse(error.error).message });
        });
    };
});
