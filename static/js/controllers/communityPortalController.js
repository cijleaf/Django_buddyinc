var appControllers = angular.module('mySunBuddy.controllers');
//Finish Sign-Up Portal
appControllers.controller('communityPortalController', function($scope, $rootScope, $timeout, $location, API, Upload,
    $uibModal, Alert, utils, $cookies, $window, ConfigURLs, currentUser, $route, installationService) {

    $rootScope.installation = [];

    $scope.role = $route.current.$$route.role;

    $scope.saveButton = true;

    $scope.profile = {};
    angular.extend($scope.profile, currentUser.profile);

    $scope.viewInstallations = function() {
        API.viewInstallations().$promise.then(function(installations) {
            var installation_list = [];
            angular.forEach(installations, function(data) {
                var installation_obj = {
                    "id": data.id,
                    "info": {
                        "id": data.id,
                        "name": data.name,
                        "state": data.state,
                        "zip_code": data.zip_code,
                        "community_code": data.community_code,
                        "is_active": data.is_active,
                    }
                };
                installation_list.push(installation_obj);
            });
            $scope.installations = installation_list;
        }).catch(utils.handleError);
    };
    $scope.viewInstallations();

    var creditPercent;

    if ($scope.role=='seller') {
        creditPercent = $scope.profile.credit_to_sell_percent;
    }

    $scope.solar = {
        value: creditPercent || 0,
        options: {
            from: 0,
            to: 100,
            step: 1,
            dimension: '%',
            vertical: false,
            limits: false,
            scale: ['0%', '25%', '50%', '75%', '100%']
        }
    };

    $scope.showSolarPercentSlider = false;

    //UtilityAPI
    $scope.utilityapiurl = ConfigURLs['utilityAPIPortalUrl'];

    $scope.dwollaRegisterUrl = ConfigURLs['dwollaOauthUrl'];

    $scope.dwollaLoginUrl = ConfigURLs['dwollaLoginOauthUrl'];

    $scope.googleMapsUrl = "//maps.google.com/maps/api/js?key=" + ConfigURLs.googleMapsApiKey;

    $scope.validAddresses = [];

    $scope.checking = false;

    $scope.viewSingleInstallation = function(installation) {
        API.retrieveInstallation({
            id: installation.id
        }).$promise.then(function(data) {
            $scope.getInstallation = installationService.format(data);
            angular.extend($rootScope.installation, $scope.getInstallation);
            $location.path("/Installation_Portal/" + $rootScope.installation.id);
        }).catch(utils.handleError);
    };

    $scope.editPersonalInfo = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Edit_Account.html',
            controller: 'editAccountController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function (profile) {
            $scope.profileChanges = profile;
            angular.extend($scope.profile, $scope.profileChanges);
        }, function () {});
    };

    $scope.createInstallation = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Create_Installation.html',
            controller: 'createInstallationController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function (profile) {
            $scope.profileChanges = profile;
            angular.extend($scope.profile, $scope.profileChanges);
            $scope.viewInstallations();
        }, function () {});
    };

});
