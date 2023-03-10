//
// Copyright 2016 Pixar
//
// Licensed under the Apache License, Version 2.0 (the "Apache License")
// with the following modification; you may not use this file except in
// compliance with the Apache License and the following modification to it:
// Section 6. Trademarks. is deleted and replaced with:
//
// 6. Trademarks. This License does not grant permission to use the trade
//    names, trademarks, service marks, or product names of the Licensor
//    and its affiliates, except as required to comply with Section 4(c) of
//    the License and to reproduce the content of the NOTICE file.
//
// You may obtain a copy of the Apache License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Apache License with the above modification is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied. See the Apache License for the specific
// language governing permissions and limitations under the Apache License.
//
#ifndef {{ Upper(tokensPrefix) }}_TOKENS_H
#define {{ Upper(tokensPrefix) }}_TOKENS_H

/// \file {{ libraryName }}/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// 
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
// 
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

{% if useExportAPI %}
#include "pxr/pxr.h"
#include "{{ libraryPath }}/api.h"
{% endif %}
#include "pxr/base/tf/staticData.h"
#include "pxr/base/tf/token.h"
#include <vector>

{% if useExportAPI %}
{{ namespaceOpen }}

{% endif %}

/// \class {{ tokensPrefix }}TokensType
///
/// \link {{ tokensPrefix }}Tokens \endlink provides static, efficient
/// \link TfToken TfTokens\endlink for use in all public USD API.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// {{ tokensPrefix }}Tokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.
{% if tokens %}
/// Use {{ tokensPrefix }}Tokens like so:
///
/// \code
///     gprim.GetMyTokenValuedAttr().Set({{ tokensPrefix }}Tokens->{{ tokens[0].id }});
/// \endcode
{% endif %}
struct {{ tokensPrefix }}TokensType {
    {% if useExportAPI %}{{ Upper(libraryName) }}_API {% endif %}{{ tokensPrefix }}TokensType();
{% for token in tokens %}
    /// \brief "{{ token.value }}"
    /// 
    /// {{ token.desc }}
    const TfToken {{ token.id }};
{% endfor %}
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

/// \var {{ tokensPrefix }}Tokens
///
/// A global variable with static, efficient \link TfToken TfTokens\endlink
/// for use in all public USD API.  \sa {{ tokensPrefix }}TokensType
extern{% if useExportAPI %} {{ Upper(libraryName) }}_API{% endif %} TfStaticData<{{ tokensPrefix }}TokensType> {{ tokensPrefix }}Tokens;
{% if useExportAPI %}

{{ namespaceClose }}
{% endif %}

#endif
