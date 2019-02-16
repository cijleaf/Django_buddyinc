var appControllers = angular.module('mySunBuddy.controllers');
//Sign Up
appControllers.controller('signUpController', function($scope, $rootScope, $timeout, $location, $uibModal, API, Upload,
                                                       Alert, utils, $cookies, $window, currentUser, $route,
                                                       behaviorExperiment, $analytics) {

    //Modal
    $scope.showSignInModal = function() {
        var modalInstance = $uibModal.open({
            animation: false,
            templateUrl: 'static/templates/Modal_Sign_In.html',
            controller: 'signInController',
            resolve: {
                profile: function () {
                    return $scope.profile;
                }
            }
        });
        modalInstance.result.then(function () {
        }, function () {});
    };

    $scope.submitted = false;



    //Step
    $scope.user = {};

    $scope.role = $route.current.$$route.role;

    $scope.validAddresses = [];

    $scope.checking = false;

    //for modal of editSolarProduction
    $scope.module = {
        summary: {
            solar: {}
        }
    };

    $scope.signup = function() {
        if (!$scope.signupForm.$valid) {
            $scope.submitted = true;
            return
        }
        var user = $scope.user;
        user.role = $scope.role;
        user.landing_page = behaviorExperiment.getChosenVariationLabel();
        Upload.upload({
            url: '/api/register',
            method: 'POST',
            data: user
        }).then(function(resp) {
            //$location.path("/Confirm-email");
            API.login({
                login: user.email,
                password: user.password
            }).$promise
                .then(function(profile) {
                    $analytics.eventTrack(user.role + ' signup', {
                        category: 'signup',
                        label: user.landing_page
                    });
                    currentUser.update(profile);
                    if (currentUser.profile.role == 'seller') {
                        $location.path("/Seller_Account_Portal");
                    } else {
                        $location.path("/Buyer_Account_Portal");
                    }
                }).catch(function(error) {
                    var errors = utils.parseError(error);
                    $scope.result = 'error';
                    if (errors.length) {
                        if (errors[0] == 'Email address is not verified.') {
                            $scope.result = 'verified';
                        } else if (errors[0] == 'User account is disabled.') {
                            $scope.result = 'disabled';
                        } else {
                          $scope.result = '';
                        }
                    }
                });
        }).catch(utils.handleError);
    };
});
