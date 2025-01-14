Proxy Settings
==============

.. tags:: settings

Examples
::::::::

Defaults
--------

Here is an example with defaults, and some stub values for required or sequence-based settings:

.. literalinclude:: ./examples/reference.yml
    :language: yaml

With multiple remote endpoints
------------------------------

Here is an example showing how to configure multiple remote endpoints:

.. literalinclude:: ./examples/full.yml
    :language: yaml

Reference
:::::::::

Implementation (python): :class:`ProxySettings <harp_apps.proxy.settings.ProxySettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/ProxySettings


.endpoints[]
------------

Implementation (python): :class:`EndpointSettings <harp_apps.proxy.settings.EndpointSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/EndpointSettings

.endpoints[].remote
-------------------

Implementation (python): :class:`RemoteSettings <harp_apps.proxy.settings.RemoteSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/RemoteSettings

.endpoints[].remote.endpoint
----------------------------

Implementation (python): :class:`RemoteEndpointSettings <harp_apps.proxy.settings.RemoteEndpointSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/RemoteEndpointSettings

.endpoints[].remote.probe
-------------------------

Implementation (python): :class:`RemoteProbeSettings <harp_apps.proxy.settings.RemoteProbeSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/RemoteProbeSettings

...liveness
-----------

Can be set at the remote enpoint level or at the remote level. If all levels are set to inherit, will use a naive
implementation by default.

Implementation (python): :class:`BaseLivenessSettings <harp_apps.proxy.settings.liveness.base.BaseLivenessSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/BaseLivenessSettings

This is the base type, actual implementation will depend on choosen type, documented below in order of complexity.

Inherit
.......

Implementation (python): :class:`InheritLivenessSettings <harp_apps.proxy.settings.liveness.base.BaseLivenessSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/InheritLivenessSettings

Ignore
......

Implementation (python): :class:`IgnoreLivenessSettings <harp_apps.proxy.settings.liveness.base.BaseLivenessSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/IgnoreLivenessSettings

Naive
.....

Implementation (python): :class:`NaiveLivenessSettings <harp_apps.proxy.settings.liveness.base.BaseLivenessSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/NaiveLivenessSettings

Leaky Bucket
............

Implementation (python): :class:`LeakyBucketLivenessSettings <harp_apps.proxy.settings.liveness.base.BaseLivenessSettings>`

.. jsonschema:: ./schema.json
   :pointer: /$defs/LeakyBucketLivenessSettings


Class Diagram
:::::::::::::

.. todo::

    This should be completely autogenerated, for now it was made using ``pyreverse harp_apps.proxy.settings -o dot`` for
    inheritance, followed by a manual edition to add relations. We can use this base but then introspect pydantic models
    to make sure we have all the relations, amnual edit is error prone.

.. graphviz:: settings.dot
