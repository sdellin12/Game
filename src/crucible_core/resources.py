"""Exact resource payments and own-Start maintenance; no saved-state schema."""
from dataclasses import dataclass, replace


class ResourceError(ValueError):
    pass


@dataclass(frozen=True)
class ResourcePool:
    natural_capacity: int = 2
    permanent_bonus: int = 0
    available: int = 0
    own_starts: int = 0


@dataclass(frozen=True)
class Payment:
    ordinary: int
    token_ids: tuple[str, ...] = ()


def validate_pool(pool):
    if type(pool) is not ResourcePool or any(type(x) is not int or x < 0 for x in
            (pool.natural_capacity, pool.permanent_bonus, pool.available, pool.own_starts)):
        raise ResourceError('invalid resource pool')
    if not 2 <= pool.natural_capacity <= 10:
        raise ResourceError('natural capacity must be 2 through 10')


def start_resources(pool, ongoing_bonus=0):
    validate_pool(pool)
    if type(ongoing_bonus) is not int or ongoing_bonus < 0:
        raise ResourceError('invalid ongoing capacity bonus')
    capacity=min(10, pool.natural_capacity + (pool.own_starts > 0))
    return replace(pool, natural_capacity=capacity, own_starts=pool.own_starts+1,
                   available=capacity+pool.permanent_bonus+ongoing_bonus)


def pay_resources(pool, cost, payment, tokens):
    """tokens is the caller-filtered (controlled token ID, value) tuple."""
    validate_pool(pool)
    if type(cost) is not int or cost < 0 or type(payment) is not Payment:
        raise ResourceError('invalid cost/payment')
    if type(tokens) is not tuple or any(type(t) is not tuple or len(t)!=2 or
            type(t[0]) is not str or not t[0] or type(t[1]) is not int or t[1]<1 for t in tokens):
        raise ResourceError('invalid token inventory')
    inventory=dict(tokens)
    if len(inventory)!=len(tokens):
        raise ResourceError('duplicate token inventory')
    if (type(payment.ordinary) is not int or not 0<=payment.ordinary<=pool.available
            or type(payment.token_ids) is not tuple or any(type(t) is not str for t in payment.token_ids)
            or len(set(payment.token_ids))!=len(payment.token_ids)
            or any(t not in inventory for t in payment.token_ids)):
        raise ResourceError('unavailable or duplicated payment source')
    if payment.ordinary+sum(inventory[t] for t in payment.token_ids)!=cost:
        raise ResourceError('payment must equal the locked cost exactly')
    return replace(pool, available=pool.available-payment.ordinary)
