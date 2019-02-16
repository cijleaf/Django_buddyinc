//used in sign up section 1 and modal edit account
angular.module('mySunBuddy.common')
.directive('domainEmail', function ($parse) {
    return {
        require: '?ngModel',
        restrict: 'A',
        link: function (scope, elem, attrs, ctrl) {
            if (!ctrl) {
                //Match validation requires ngModel to be on the element
                return;
            }
             ctrl.$validators.domainEmail = function(){
              return ctrl.$isEmpty(ctrl.$viewValue)||/^[a-zA-Z]+[a-zA-Z0-9._]+@[a-zA-Z]+\.[a-zA-Z.]{2,5}$/.test(ctrl.$viewValue);
            };
        }
    };
});