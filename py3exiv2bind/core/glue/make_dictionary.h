//
// Created by Borchers, Henry Samuel on 11/6/17.
//

#ifndef PYEXIV2BIND_MAKE_DICTIONARY_H
#define PYEXIV2BIND_MAKE_DICTIONARY_H
#include <unordered_map>

template<typename T1>
std::unordered_map<std::string, std::string> make_dictionary(const T1 &data) {

    if(data.empty()){
        return std::unordered_map<std::string, std::string>();
    }

    std::unordered_map<std::string, std::string> metadata;
    auto end = data.end();
    for (auto md = data.begin(); md != end; md++){
        metadata[md->key()] = md->value().toString();
    }
    return metadata;
};

#endif //PYEXIV2BIND_MAKE_DICTIONARY_H
