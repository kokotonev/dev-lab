export default function RegisterPage() {
    return (
        <div className="max-w-sm mx-auto">
            <h2 className="mb-6 text-2xl text-center">Register Page</h2>
            <form className="flex flex-col gap-3">
                <input type="email" placeholder="Email" />
                <input type="password" placeholder="Password" />
                <input type="password" placeholder="Confirm Password" />
                <button type="submit" className="mt-3">Register</button>
            </form>
        </div>
    )
}
