.. vim: tw=80 lbr

Contributing
------------

As mentioned in the README, this project is stable and mature. It's not
receiving significant ongoing investment, but well-formed fixes and improvements
are welcome. "Well-formed" in this context primarily means that it is fully
backward-compatible and includes documentation and test coverage. Improvements
that can just as well exist as external plugins should be implemented as such.

Before checking in, always run ``hatch run check`` to run linters and the test
suite. The CI configuration will actually run ``hatch run test:run``, which will
test across multiple Python/Django versions for completeness. If you get linter
errors, you may be able to fix them with ``hatch run fix``.

An important thing to remember is that this is a framework that supports a wide
range of plugins. There's only one rule for a plugin: it must inherit from
`django_otp.models.Device` and implement one key method. The project provides a
collection of mixins and other abstract model classes to help with common
functionality, but they are all optional.

The key takeaway here is that when considering backward-compatibility, you can
assume virtually nothing. In particular, note that adding a new model field to
an abstract model class is a breaking change and should be avoided at almost all
costs. Updating an existing abstract model in django-otp will trigger the need
for migrations in all projects that rely on it, leading to a special kind of
dependency hell.

New standard functionality options can be added by defining additional mixins if
necessary. Stub methods may be added to the root Device class to define common
interfaces for such features.

As always, remember that writing the code is often the least part of making a
change. Understanding the problem and alternative approaches, writing good
documentation, making a testing strategy, and demonstrating backward
compatibility collectively tend to dwarf actually typing out the implementation.
