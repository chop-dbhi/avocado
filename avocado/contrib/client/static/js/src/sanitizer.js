var SearchSanitizer = {
    regexes: {
        /*
        ** Common regular expressions for stripping query strings of insignificant
        ** characters, stop words and special characters.
        */
        truncateWhiteSpace: [(/\s{2,}/g), ' '],
    
        removeNonAlphaNumeric: [(/[^\sA-Za-z0-9]/g), ''],

        removeStopWords: [(/\b(a|able|about|across|after|all|almost|also|am|among|an|and|any|are|as|at|be|because|been|but|by|can|cannot|could|dear|did|do|does|either|else|ever|every|for|from|get|got|had|has|have|he|her|hers|him|his|how|however|i|if|in|into|is|it|its|just|least|let|like|likely|may|me|might|most|must|my|neither|no|nor|not|of|off|often|on|only|or|other|our|own|rather|said|say|says|she|should|since|so|some|than|that|the|their|them|then|there|these|they|this|tis|to|too|twas|us|wants|was|we|were|what|when|where|which|while|who|whom|why|will|with|would|yet|you|your)\b/g), ''],
    
        trimRightWhiteSpace: [(/^\s+/), ''],
    
        trimLeftWhiteSpace: [(/\s+$/), '']
    },

    clean: function(str) {
        for (var key in this.regexes) {
            var e = this.regexes[key];
            str = str.replace(e[0], e[1]);
        }
        return str;
    }
};