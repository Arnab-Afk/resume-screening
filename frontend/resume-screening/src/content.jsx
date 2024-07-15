export default function Content({data}) {
    const [improvements ,setImprovements]=([]);
    const [views , setViews]=([]);
    const [requirements , setRequirements]=([]);
    console.log(data);
    return (
      <div className="bg-white py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:mx-0 lg:max-w-none">
            <p className="text-base font-semibold leading-7 text-indigo-600">Deploy faster</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Requirements</h1>
            <div className="mt-10 grid max-w-xl grid-cols-1 gap-8 text-base leading-7 text-gray-700 lg:max-w-none lg:grid-cols-2">
              {/* <div>
                {improvements.map((improvement, index) => (
                    <p className="mt-8">
                      {improvement}
                  </p>
                    ))}
              </div>
              <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Views</h1>
              <div>
                {views.map((view, index) => (
                    <p className="mt-8">
                      {view}
                  </p>
                    ))}
              </div>
              <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Requirements</h1>
                <div>
                {requirements.map((requirement, index) => (
                    <p className="mt-8">
                      {requirement}
                  </p>
                    ))}
                    </div> */}

              {data.map((item, index) => (
                <div key={index}>
                  <p className="mt-8">
                    {item}
                  </p>
                </div>
              ))}
            </div>
            <div className="mt-10 flex">
              <a
                href="#"
                className="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Get started
              </a>
            </div>
          </div>
        </div>
        
      </div>
    )
  }
  