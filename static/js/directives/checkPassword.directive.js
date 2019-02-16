(function() {
  'use strict';

  angular.module('mySunBuddy.common')
    .directive('checkPassword',
      function() {
        return {
          template:
              // '<div class="pwd_info {{hiddenClass}}">' +
              // '     <p class="invalid">Password must be requirements</p>' +
              // '     <ul>' +
              // '         <li class="{{letterValidClass}}">At least <strong>one letter</strong></li>' +
              // '         <li class="{{capitalValidClass}}">At least <strong>one capital letter</strong></li>' +
              // '         <li class="{{numberValidClass}}">At least <strong>one number</strong></li>' +
              // '         <li class="{{lengthValidClass}}">Be at least <strong>8 characters</strong></li>' +
              // '         <li class="{{specialValidClass}}">At least <strong>one special letter</strong></li>' +
              // '     </ul>' +
              // '</div>',
              '<p class="error-info {{hiddenClass}}">Password must include: ' +
                  '<span class="{{letterValidClass}}">at least one letter, </span>' +
                  '<span class="{{capitalValidClass}}">at least capital letter, </span>' +
                  '<span class="{{numberValidClass}}">at least one number, </span>' +
                  '<span class="{{lengthValidClass}}">be at least 8 characters, </span>' +
                  '<span class="{{specialValidClass}}">at least one special letter.</span>' +
              '</p>',

          restrict: 'A',

          scope: {
            pwd: '=checkPassword'
          },

          link: function(scope) {
              scope.hiddenClass = 'hidden';
              scope.letterValidClass = 'valid';
              scope.capitalValidClass = 'valid';
              scope.numberValidClass = 'valid';
              scope.lengthValidClass = 'valid';
              scope.specialValidClass = 'valid';

              var checkValid = function (pwd) {
                  var is_valid = true;

                  if (!pwd) {
                      return true
                  }

                  if( pwd.length < 8 ) {
                      scope.lengthValidClass = 'invalid';
                      is_valid = false;
                  }else{
                      scope.lengthValidClass = 'valid'
                  }

                  if( pwd.match(/[a-z]/g) ) {
                      scope.letterValidClass = 'valid';
                  }else{
                      scope.letterValidClass = 'invalid';
                      is_valid = false;
                  }

                  if( pwd.match(/[A-Z]/g) ) {
                      scope.capitalValidClass = 'valid'
                  }else{
                      scope.capitalValidClass = 'invalid';
                      is_valid = false;
                  }

                  if( pwd.match(/\d/g) ) {
                      scope.numberValidClass = 'valid'
                  }else{
                      scope.numberValidClass = 'invalid';
                      is_valid = false;
                  }

                  if( pwd.match(/[!@#$%^&*()\-_=+{};:,<.>]/g) ) {
                      scope.specialValidClass = 'valid'
                  }else{
                      scope.specialValidClass = 'invalid';
                      is_valid = false;
                  }

                  return is_valid

              };

              scope.$watch('pwd', function(newval) {

                    if (checkValid(scope.pwd)){
                        scope.hiddenClass = 'hidden';
                    }else{
                        scope.hiddenClass = 'visible';
                    }

              });
          }
        };
      });
})();
